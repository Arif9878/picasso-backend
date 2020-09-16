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

INSERT INTO public.satuan_kerjas (id, parent_id, name_parent, name_satuan_kerja, description, created_at, created_by, updated_at, updated_by) VALUES ('2658e4f3-a102-48bc-8d3f-f86faa50b371', '', '', 'Analisis', '', '2020-07-01 01:20:58.905106+07', 'admin@example.com', '2020-07-01 01:20:58.905106+07', '');
INSERT INTO public.satuan_kerjas (id, parent_id, name_parent, name_satuan_kerja, description, created_at, created_by, updated_at, updated_by) VALUES ('91833e02-60bb-463b-bca2-bbc34de501ed', '', '', 'Data', '', '2020-07-01 01:21:05.009426+07', 'admin@example.com', '2020-07-01 01:21:05.009426+07', '');
INSERT INTO public.satuan_kerjas (id, parent_id, name_parent, name_satuan_kerja, description, created_at, created_by, updated_at, updated_by) VALUES ('462a42d6-0aaa-4a19-8999-2c20c946f68d', '', '', 'IT Dev', '', '2020-07-01 01:21:16.407537+07', 'admin@example.com', '2020-07-01 01:21:16.407537+07', '');
INSERT INTO public.satuan_kerjas (id, parent_id, name_parent, name_satuan_kerja, description, created_at, created_by, updated_at, updated_by) VALUES ('a8cf3cc0-7636-4584-95c5-0fa09b1183e4', '', '', 'Implementasi dan Pengelolaan', '', '2020-07-01 01:21:39.006942+07', 'admin@example.com', '2020-07-01 01:21:39.006942+07', '');
INSERT INTO public.satuan_kerjas (id, parent_id, name_parent, name_satuan_kerja, description, created_at, created_by, updated_at, updated_by) VALUES ('7ca21079-2d16-4a43-a0bd-e367ec3b4834', '', '', 'Komunikasi dan Konten', '', '2020-07-01 01:22:10.570721+07', 'admin@example.com', '2020-07-01 01:22:10.570721+07', '');


--
-- TOC entry 2930 (class 0 OID 16393)
-- Dependencies: 203
-- Data for Name: jabatans; Type: TABLE DATA; Schema: public; Owner: adminpostgre
--

INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('47a8cef4-9450-488a-9874-f22e021c33a4', '91833e02-60bb-463b-bca2-bbc34de501ed', 'Data', 'Administration', '', '2020-07-01 01:30:25.223789+07', 'admin@example.com', '2020-07-01 01:30:25.223789+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('9b1893e3-c393-4a60-824c-ef1b4280ad1d', '91833e02-60bb-463b-bca2-bbc34de501ed', 'Data', 'Business Intelligence Developer', '', '2020-07-01 01:30:33.594242+07', 'admin@example.com', '2020-07-01 01:30:33.594242+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('b3abd90f-2a4d-4c6f-986c-32898a6a752d', '91833e02-60bb-463b-bca2-bbc34de501ed', 'Data', 'Data Analyst', '', '2020-07-01 01:30:39.548098+07', 'admin@example.com', '2020-07-01 01:30:39.548098+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('230dee8a-49b4-4a14-98a0-85880787f121', '91833e02-60bb-463b-bca2-bbc34de501ed', 'Data', 'Data Engineer', '', '2020-07-01 01:30:45.297076+07', 'admin@example.com', '2020-07-01 01:30:45.297076+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('23433d79-5a6e-4ca3-bb48-0ab64598ba9c', '91833e02-60bb-463b-bca2-bbc34de501ed', 'Data', 'Data Entry', '', '2020-07-01 01:30:50.925043+07', 'admin@example.com', '2020-07-01 01:30:50.925043+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('70f6ca25-9314-400e-aa9e-339fa9101bde', '91833e02-60bb-463b-bca2-bbc34de501ed', 'Data', 'Koordinator Bidang Analisis', '', '2020-07-01 01:30:58.218612+07', 'admin@example.com', '2020-07-01 01:30:58.218612+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('c26acd57-215f-4a8c-a17f-f1d3a05b9c14', '2658e4f3-a102-48bc-8d3f-f86faa50b371', 'Analisis', 'Business Analyst', '', '2020-07-01 01:33:15.718368+07', 'admin@example.com', '2020-07-01 01:33:15.718368+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('e7528ef5-53ef-439e-b192-370d3f0ded00', '2658e4f3-a102-48bc-8d3f-f86faa50b371', 'Analisis', 'Junior Product Manager', '', '2020-07-01 01:33:21.813199+07', 'admin@example.com', '2020-07-01 01:33:21.813199+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('2a561c5f-5069-4a38-b3c9-d2e29bb963a5', '2658e4f3-a102-48bc-8d3f-f86faa50b371', 'Analisis', 'Product Manager', '', '2020-07-01 01:33:26.883396+07', 'admin@example.com', '2020-07-01 01:33:26.883396+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('930c6134-59c1-4ee7-84ea-286f8a66403f', '2658e4f3-a102-48bc-8d3f-f86faa50b371', 'Analisis', 'UI Designer', '', '2020-07-01 01:33:32.714687+07', 'admin@example.com', '2020-07-01 01:33:32.714687+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('80bd9673-bee6-4d6c-8f04-f8d755615dc5', '2658e4f3-a102-48bc-8d3f-f86faa50b371', 'Analisis', 'UX Researcher', '', '2020-07-01 01:33:37.171498+07', 'admin@example.com', '2020-07-01 01:33:37.171498+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('418ac050-f57d-46ff-847c-d93551d62897', '2658e4f3-a102-48bc-8d3f-f86faa50b371', 'Analisis', 'Koordinator Bidang Analisis', '', '2020-07-01 01:33:42.408886+07', 'admin@example.com', '2020-07-01 01:33:42.408886+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('2a74ef03-5a2b-4a4b-83f9-7aceabe1b84b', '7ca21079-2d16-4a43-a0bd-e367ec3b4834', 'Komunikasi dan Konten', 'Content Officer', '', '2020-07-01 01:35:57.881339+07', 'admin@example.com', '2020-07-01 01:35:57.881339+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('fa25c583-511e-41fd-bfc8-8ad24b29012e', '7ca21079-2d16-4a43-a0bd-e367ec3b4834', 'Komunikasi dan Konten', 'Content Strategist', '', '2020-07-01 01:36:05.371454+07', 'admin@example.com', '2020-07-01 01:36:05.371454+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('a963f162-111e-4517-8a25-5edeca4d5643', '7ca21079-2d16-4a43-a0bd-e367ec3b4834', 'Komunikasi dan Konten', 'Koordinator Bidang Analisis', '', '2020-07-01 01:36:11.92459+07', 'admin@example.com', '2020-07-01 01:36:11.92459+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('36c502fb-1d1b-475b-894b-01a8c8d702fd', 'a8cf3cc0-7636-4584-95c5-0fa09b1183e4', 'Implementasi dan Pengelolaan', 'Front Office (Tenaga Teknis)', '', '2020-07-01 01:38:42.613787+07', 'admin@example.com', '2020-07-01 01:38:42.613787+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('15f2870b-9454-433a-9e8c-556ade560111', 'a8cf3cc0-7636-4584-95c5-0fa09b1183e4', 'Implementasi dan Pengelolaan', 'Monitoring Officer', '', '2020-07-01 01:38:47.7319+07', 'admin@example.com', '2020-07-01 01:38:47.7319+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('97adc6c8-4d3f-4d31-8a52-51c211a5137b', 'a8cf3cc0-7636-4584-95c5-0fa09b1183e4', 'Implementasi dan Pengelolaan', 'Project Officer', '', '2020-07-01 01:38:53.014739+07', 'admin@example.com', '2020-07-01 01:38:53.014739+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('d6d0e59c-7d61-4978-bd34-001a58fd9a48', 'a8cf3cc0-7636-4584-95c5-0fa09b1183e4', 'Implementasi dan Pengelolaan', 'Koordinator Bidang Analisis', '', '2020-07-01 01:39:01.956585+07', 'admin@example.com', '2020-07-01 01:39:01.956585+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('5bcd0c67-7713-44bd-90ae-66976d1d1420', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'DevOps / SRE Engineer', '', '2020-07-01 01:42:27.015343+07', 'admin@example.com', '2020-07-01 01:42:27.015343+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('100aae20-68da-4966-b844-0bb166d06933', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'IT Helpdesk', '', '2020-07-01 01:42:42.146972+07', 'admin@example.com', '2020-07-01 01:42:42.146972+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('173f98ed-c084-4fa8-8eba-b371813aba07', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'Junior Software Programmer - Backend Engineer', '', '2020-07-01 01:42:48.668225+07', 'admin@example.com', '2020-07-01 01:42:48.668225+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('558372b2-c2a4-4564-a043-629211411486', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'Junior Software Programmer - Frontend Engineer', '', '2020-07-01 01:42:56.723409+07', 'admin@example.com', '2020-07-01 01:42:56.723409+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('3aeeb9b5-9c08-406d-bec3-89a474960949', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'Koordinator Bidang Analisis', '', '2020-07-01 01:43:02.613783+07', 'admin@example.com', '2020-07-01 01:43:02.613783+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('47ca4c1a-e115-436e-b140-d5ce4e022e61', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'Network Engineer', '', '2020-07-01 01:43:09.657727+07', 'admin@example.com', '2020-07-01 01:43:09.657727+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('54f161e9-fb61-4516-b173-5978ad39dd41', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'Software Programmer - Backend Engineer', '', '2020-07-01 01:43:15.088458+07', 'admin@example.com', '2020-07-01 01:43:15.088458+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('bb161daf-892b-458a-bca3-e66d5eb39706', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'Software Programmer - Mobile Engineer', '', '2020-07-01 01:43:19.780374+07', 'admin@example.com', '2020-07-01 01:43:19.780374+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('0b951b89-a9d5-4b8f-8838-f57893370418', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'Software QA', '', '2020-07-01 01:43:26.898021+07', 'admin@example.com', '2020-07-01 01:43:26.898021+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('03cf8cdf-2d26-42fb-9257-2b5dc91417f3', '2658e4f3-a102-48bc-8d3f-f86faa50b371', 'Analisis', 'Human Resources', '', '2020-07-01 01:57:14.883755+07', 'admin@example.com', '2020-07-01 01:57:14.883755+07', '');
INSERT INTO public.jabatans (id, satuan_kerja_id, name_satuan_kerja, name_jabatan, description, created_at, created_by, updated_at, updated_by) VALUES ('04df5d61-52fd-484f-99ce-cbe521c81cfe', '462a42d6-0aaa-4a19-8999-2c20c946f68d', 'IT Dev', 'Technical Writer', '', '2020-07-01 01:43:32.453193+07', 'admin@example.com', '2020-07-11 18:45:39.428814+07', '');

-- Completed on 2020-07-16 17:17:47 WIB

--
-- PostgreSQL database dump complete
--
