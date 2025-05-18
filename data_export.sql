--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: arabic_ci; Type: COLLATION; Schema: public; Owner: postgres
--

CREATE COLLATION public.arabic_ci (provider = icu, deterministic = false, locale = 'ar-u-ks-level2');


ALTER COLLATION public.arabic_ci OWNER TO postgres;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: arabic_similarity(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.arabic_similarity(text, text) RETURNS real
    LANGUAGE plpgsql IMMUTABLE
    AS $_$
BEGIN
    RETURN similarity(
        regexp_replace($1, '[^\u0600-\u06FF]', '', 'g'),
        regexp_replace($2, '[^\u0600-\u06FF]', '', 'g')
    );
END;
$_$;


ALTER FUNCTION public.arabic_similarity(text, text) OWNER TO postgres;

--
-- Name: arabic_simple_search(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.arabic_simple_search(str1 text, str2 text) RETURNS real
    LANGUAGE plpgsql IMMUTABLE
    AS $$
DECLARE
    max_len int := greatest(length(str1), length(str2));
    matches int := 0;
BEGIN
    FOR i IN 1..max_len LOOP
        IF substring(str1 FROM i FOR 1) = substring(str2 FROM i FOR 1) THEN
            matches := matches + 1;
        END IF;
    END LOOP;
    
    RETURN matches::float / max_len;
END;
$$;


ALTER FUNCTION public.arabic_simple_search(str1 text, str2 text) OWNER TO postgres;

--
-- Name: clean_arabic_search(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.clean_arabic_search(str1 text, str2 text) RETURNS real
    LANGUAGE plpgsql IMMUTABLE
    AS $$
BEGIN
    RETURN enhanced_arabic_search(
        remove_diacritics(str1 COLLATE "C"),
        remove_diacritics(str2 COLLATE "C")
    );
END;
$$;


ALTER FUNCTION public.clean_arabic_search(str1 text, str2 text) OWNER TO postgres;

--
-- Name: clean_invalid_arabic(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.clean_invalid_arabic() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- ???????? ?????? ???????? COLLATE "C"
    BEGIN
        DELETE FROM products_product
        WHERE name_ar IS NULL
           OR name_ar COLLATE "C" LIKE '%?%'
           OR name_ar COLLATE "C" LIKE '%?%';
    EXCEPTION WHEN OTHERS THEN
        -- ???????? ??????? ???????? ??????? ???????
        DELETE FROM products_product
        WHERE name_ar IS NULL
           OR convert_to(name_ar, 'UTF8')::text LIKE '%?%'
           OR convert_to(name_ar, 'UTF8')::text LIKE '%?%';
    END;
END;
$$;


ALTER FUNCTION public.clean_invalid_arabic() OWNER TO postgres;

--
-- Name: enhanced_arabic_search(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.enhanced_arabic_search(str1 text, str2 text) RETURNS real
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $$
BEGIN
    RETURN similarity(
        str1 COLLATE "C",
        str2 COLLATE "C"
    );
END;
$$;


ALTER FUNCTION public.enhanced_arabic_search(str1 text, str2 text) OWNER TO postgres;

--
-- Name: final_arabic_search(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.final_arabic_search(str1 text, str2 text) RETURNS real
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $$
BEGIN
    RETURN enhanced_arabic_search(
        simple_remove_diacritics(str1),
        simple_remove_diacritics(str2)
    );
END;
$$;


ALTER FUNCTION public.final_arabic_search(str1 text, str2 text) OWNER TO postgres;

--
-- Name: remove_diacritics(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.remove_diacritics(input text) RETURNS text
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $$
BEGIN
    RETURN regexp_replace(input, '[????????]', '', 'g');
END;
$$;


ALTER FUNCTION public.remove_diacritics(input text) OWNER TO postgres;

--
-- Name: simple_remove_diacritics(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.simple_remove_diacritics(input text) RETURNS text
    LANGUAGE plpgsql IMMUTABLE STRICT
    AS $$
DECLARE
    result text := '';
    c text;
BEGIN
    FOR i IN 1..length(input) LOOP
        c := substring(input FROM i FOR 1);
        -- ????? ????? ???? ??????? ???????? (???? ????? ??????)
        IF c NOT IN ('?','?','?','?','?','?','?','?','?') THEN
            result := result || c;
        END IF;
    END LOOP;
    RETURN result;
END;
$$;


ALTER FUNCTION public.simple_remove_diacritics(input text) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: products_product; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_product (
    id integer,
    name_ar text COLLATE pg_catalog."C",
    name_en text
);


ALTER TABLE public.products_product OWNER TO postgres;

--
-- Name: products_product_backup; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products_product_backup (
    id integer,
    name_ar character varying(255) COLLATE public.arabic_ci,
    name_en character varying(255),
    description_ar text COLLATE public.arabic_ci,
    description_en text
);


ALTER TABLE public.products_product_backup OWNER TO postgres;

--
-- Data for Name: products_product; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products_product (id, name_ar, name_en) FROM stdin;
1	?????? ?????	Dark Chocolate
2	???????? ??????	Milk Chocolate
3	??????? ???????	Hazelnut Chocolate
4	??? ????	Green Tea
5	???? ?????	Arabic Coffee
\.


--
-- Data for Name: products_product_backup; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products_product_backup (id, name_ar, name_en, description_ar, description_en) FROM stdin;
1	??????	Protein	???? ?????	Nutritional supplement
2	????????	Chocolate	???? ?????	Delicious candy
\.


--
-- Name: idx_products_name_ar; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_name_ar ON public.products_product USING gin (name_ar public.gin_trgm_ops);


--
-- PostgreSQL database dump complete
--

