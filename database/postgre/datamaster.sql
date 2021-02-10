--
-- PostgreSQL database dump
--

-- Dumped from database version 12.3
-- Dumped by pg_dump version 12.2

-- Started on 2020-09-06 21:30:55 WIB

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

\connect datamaster

--
-- TOC entry 203 (class 1259 OID 16393)
-- Name: jabatans; Type: TABLE; Schema: public; Owner: adminpostgre
--

CREATE TABLE public.jabatans (
    id uuid NOT NULL,
    satuan_kerja_id character varying(40),
    name_satuan_kerja character varying(64),
    name_jabatan character varying(64),
    description text,
    created_at timestamp with time zone,
    created_by text,
    updated_at timestamp with time zone,
    updated_by text
);


ALTER TABLE public.jabatans OWNER TO adminpostgre;

--
-- TOC entry 202 (class 1259 OID 16387)
-- Name: satuan_kerjas; Type: TABLE; Schema: public; Owner: adminpostgre
--

CREATE TABLE public.satuan_kerjas (
    id uuid NOT NULL,
    parent_id character varying(40),
    name_parent character varying(64),
    name_satuan_kerja character varying(64),
    description character varying(255),
    created_at timestamp with time zone,
    created_by text,
    updated_at timestamp with time zone,
    updated_by text
);


ALTER TABLE public.satuan_kerjas OWNER TO adminpostgre;

--
-- TOC entry 2802 (class 2606 OID 16402)
-- Name: jabatans jabatans_pkey; Type: CONSTRAINT; Schema: public; Owner: adminpostgre
--

ALTER TABLE ONLY public.jabatans
    ADD CONSTRAINT jabatans_pkey PRIMARY KEY (id);


--
-- TOC entry 2798 (class 2606 OID 16400)
-- Name: satuan_kerjas satuan_kerjas_pkey; Type: CONSTRAINT; Schema: public; Owner: adminpostgre
--

ALTER TABLE ONLY public.satuan_kerjas
    ADD CONSTRAINT satuan_kerjas_pkey PRIMARY KEY (id);


--
-- TOC entry 2799 (class 1259 OID 16405)
-- Name: idx_jabatans_name_jabatan; Type: INDEX; Schema: public; Owner: adminpostgre
--

CREATE INDEX idx_jabatans_name_jabatan ON public.jabatans USING btree (name_jabatan);


--
-- TOC entry 2800 (class 1259 OID 16404)
-- Name: idx_jabatans_satuan_kerja_id; Type: INDEX; Schema: public; Owner: adminpostgre
--

CREATE INDEX idx_jabatans_satuan_kerja_id ON public.jabatans USING btree (satuan_kerja_id);


--
-- TOC entry 2796 (class 1259 OID 16403)
-- Name: idx_satuan_kerjas_parent_id; Type: INDEX; Schema: public; Owner: adminpostgre
--

CREATE INDEX idx_satuan_kerjas_parent_id ON public.satuan_kerjas USING btree (parent_id);



--
-- TOC entry 2929 (class 0 OID 16387)
-- Dependencies: 202
-- Data for Name: satuan_kerjas; Type: TABLE DATA; Schema: public; Owner: adminpostgre
--

INSERT INTO public.satuan_kerjas (id, parent_id, name_parent, name_satuan_kerja, description, created_at, created_by, updated_at, updated_by) VALUES ('862a42d6-0aaa-4a19-8999-2p20o946f68d', '', '', 'IT Dev', '', '2020-07-01 01:21:16.407537+07', 'admin@example.com', '2020-07-01 01:21:16.407537+07', '');

--
-- TOC entry 2930 (class 0 OID 16393)
-- Dependencies: 203
-- Data for Name: jabatans; Type: TABLE DATA; Schema: public; Owner: adminpostgre
--

INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('54f161e9-fb61-4516-b173-5978ad39dd41', '862a42d6-0aaa-4a19-8999-2p20o946f68d', 'IT Dev', 'Software Programmer - Backend Engineer', '', '2020-07-01 01:43:15.088458+07', 'admin@example.com', '2020-07-01 01:43:15.088458+07', '');

-- Completed on 2020-07-16 17:17:47 WIB

--
-- PostgreSQL database dump complete
--
