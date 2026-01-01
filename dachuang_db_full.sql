--
-- PostgreSQL database dump
--

\restrict vp9ptfVMwPFzmfZErZvFRD0BpUOIEpyh0Z3sa7BtvCrRfIifkRpKfMo8cybCSxS

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

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

ALTER TABLE IF EXISTS ONLY public.workflow_nodes DROP CONSTRAINT IF EXISTS workflow_nodes_workflow_id_411643ef_fk_workflow_configs_id;
ALTER TABLE IF EXISTS ONLY public.workflow_nodes DROP CONSTRAINT IF EXISTS workflow_nodes_review_template_id_bf4b0c22_fk_review_te;
ALTER TABLE IF EXISTS ONLY public.workflow_configs DROP CONSTRAINT IF EXISTS workflow_configs_updated_by_id_92af6584_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.workflow_configs DROP CONSTRAINT IF EXISTS workflow_configs_created_by_id_9ce1a151_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.workflow_configs DROP CONSTRAINT IF EXISTS workflow_configs_batch_id_537df69a_fk_project_batches_id;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_user_id_92473840_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissio_permission_id_6d08dcd2_fk_auth_perm;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_user_id_f500bee5_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_group_id_2f3517aa_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.system_settings DROP CONSTRAINT IF EXISTS system_settings_updated_by_id_cf1dfbba_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.system_settings DROP CONSTRAINT IF EXISTS system_settings_batch_id_09927f7b_fk;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_reviewer_id_dbb954a8_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_review_template_id_2422673c_fk_review_templates_id;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_project_id_1ffdb6d1_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_phase_instance_id_76b853a5_fk_project_p;
ALTER TABLE IF EXISTS ONLY public.review_templates DROP CONSTRAINT IF EXISTS review_templates_updated_by_id_758db1b0_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.review_templates DROP CONSTRAINT IF EXISTS review_templates_created_by_id_4858a6a0_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.review_templates DROP CONSTRAINT IF EXISTS review_templates_batch_id_4ca9aed4_fk_project_batches_id;
ALTER TABLE IF EXISTS ONLY public.review_template_items DROP CONSTRAINT IF EXISTS review_template_item_template_id_835bbf34_fk_review_te;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_source_id_4682911e_fk_dictionary_items_id;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_level_id_8a6f1c0b_fk_dictionary_items_id;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_leader_id_aabb0912_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_discipline_id_a86933e6_fk_dictionary_items_id;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_category_id_2110ba9e_fk_dictionary_items_id;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_batch_id_67b3e4b1_fk;
ALTER TABLE IF EXISTS ONLY public.project_recycle_bin DROP CONSTRAINT IF EXISTS project_recycle_bin_restored_by_id_2665a121_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.project_recycle_bin DROP CONSTRAINT IF EXISTS project_recycle_bin_project_id_b9c359f1_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_recycle_bin DROP CONSTRAINT IF EXISTS project_recycle_bin_deleted_by_id_5d1409f9_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.project_push_records DROP CONSTRAINT IF EXISTS project_push_records_project_id_9dd8de15_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_progress DROP CONSTRAINT IF EXISTS project_progress_project_id_c9b0d403_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_progress DROP CONSTRAINT IF EXISTS project_progress_created_by_id_bfa96ce7_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.project_phase_instances DROP CONSTRAINT IF EXISTS project_phase_instances_project_id_9f3b1467_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_phase_instances DROP CONSTRAINT IF EXISTS project_phase_instances_created_by_id_7783b14c_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.project_members DROP CONSTRAINT IF EXISTS project_members_user_id_2e9d44b1_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.project_members DROP CONSTRAINT IF EXISTS project_members_project_id_bf2e42ec_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_expenditures DROP CONSTRAINT IF EXISTS project_expenditures_project_id_6c79dd16_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_expenditures DROP CONSTRAINT IF EXISTS project_expenditures_created_by_id_283ff779_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.project_expenditures DROP CONSTRAINT IF EXISTS project_expenditures_category_id_b5d751a0_fk_dictionar;
ALTER TABLE IF EXISTS ONLY public.project_change_reviews DROP CONSTRAINT IF EXISTS project_change_reviews_reviewer_id_3abd4640_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.project_change_reviews DROP CONSTRAINT IF EXISTS project_change_revie_change_request_id_7de00e2e_fk_project_c;
ALTER TABLE IF EXISTS ONLY public.project_change_requests DROP CONSTRAINT IF EXISTS project_change_requests_project_id_3231f0af_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_change_requests DROP CONSTRAINT IF EXISTS project_change_requests_created_by_id_58f7c62d_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.project_archives DROP CONSTRAINT IF EXISTS project_archives_project_id_9f133d5b_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_advisors DROP CONSTRAINT IF EXISTS project_advisors_user_id_e397bc74_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.project_advisors DROP CONSTRAINT IF EXISTS project_advisors_project_id_d2ef5924_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_achievements DROP CONSTRAINT IF EXISTS project_achievements_project_id_99c3182e_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.project_achievements DROP CONSTRAINT IF EXISTS project_achievements_achievement_type_id_1d76d968_fk_dictionar;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_related_project_id_937ebb75_fk_projects_id;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_recipient_id_e1133bac_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.login_logs DROP CONSTRAINT IF EXISTS login_logs_user_id_d31d00a1_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.expert_groups_members DROP CONSTRAINT IF EXISTS expert_groups_members_user_id_94d717a7_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.expert_groups_members DROP CONSTRAINT IF EXISTS expert_groups_member_expertgroup_id_c0b06855_fk_expert_gr;
ALTER TABLE IF EXISTS ONLY public.expert_groups DROP CONSTRAINT IF EXISTS expert_groups_created_by_id_ea191c03_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_c564eba6_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_content_type_id_c4bce8eb_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.dictionary_items DROP CONSTRAINT IF EXISTS dictionary_items_dict_type_id_08d3c96f_fk_dictionary_types_id;
ALTER TABLE IF EXISTS ONLY public.certificate_settings DROP CONSTRAINT IF EXISTS certificate_settings_updated_by_id_2d83e676_fk_users_id;
ALTER TABLE IF EXISTS ONLY public.certificate_settings DROP CONSTRAINT IF EXISTS certificate_settings_project_level_id_0ca1dab1_fk_dictionar;
ALTER TABLE IF EXISTS ONLY public.certificate_settings DROP CONSTRAINT IF EXISTS certificate_settings_project_category_id_eb459b98_fk_dictionar;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_2f476e4b_fk_django_co;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
DROP INDEX IF EXISTS public.workflow_nodes_workflow_id_411643ef;
DROP INDEX IF EXISTS public.workflow_nodes_review_template_id_bf4b0c22;
DROP INDEX IF EXISTS public.workflow_configs_updated_by_id_92af6584;
DROP INDEX IF EXISTS public.workflow_configs_created_by_id_9ce1a151;
DROP INDEX IF EXISTS public.workflow_configs_batch_id_537df69a;
DROP INDEX IF EXISTS public.users_username_e8658fc8_like;
DROP INDEX IF EXISTS public.users_user_permissions_user_id_92473840;
DROP INDEX IF EXISTS public.users_user_permissions_permission_id_6d08dcd2;
DROP INDEX IF EXISTS public.users_groups_user_id_f500bee5;
DROP INDEX IF EXISTS public.users_groups_group_id_2f3517aa;
DROP INDEX IF EXISTS public.users_employee_id_7c8e0276_like;
DROP INDEX IF EXISTS public.system_settings_updated_by_id_cf1dfbba;
DROP INDEX IF EXISTS public.system_settings_batch_id_09927f7b;
DROP INDEX IF EXISTS public.reviews_status_12ddaa_idx;
DROP INDEX IF EXISTS public.reviews_reviewer_id_dbb954a8;
DROP INDEX IF EXISTS public.reviews_review_template_id_2422673c;
DROP INDEX IF EXISTS public.reviews_project_id_1ffdb6d1;
DROP INDEX IF EXISTS public.reviews_project_1fd85d_idx;
DROP INDEX IF EXISTS public.reviews_phase_instance_id_76b853a5;
DROP INDEX IF EXISTS public.review_templates_updated_by_id_758db1b0;
DROP INDEX IF EXISTS public.review_templates_created_by_id_4858a6a0;
DROP INDEX IF EXISTS public.review_templates_batch_id_4ca9aed4;
DROP INDEX IF EXISTS public.review_template_items_template_id_835bbf34;
DROP INDEX IF EXISTS public.projects_status_6303d7_idx;
DROP INDEX IF EXISTS public.projects_source_id_4682911e;
DROP INDEX IF EXISTS public.projects_project_no_b1aacc70_like;
DROP INDEX IF EXISTS public.projects_project_b2c64d_idx;
DROP INDEX IF EXISTS public.projects_level_id_8a6f1c0b;
DROP INDEX IF EXISTS public.projects_leader_id_aabb0912;
DROP INDEX IF EXISTS public.projects_discipline_id_a86933e6;
DROP INDEX IF EXISTS public.projects_category_id_2110ba9e;
DROP INDEX IF EXISTS public.projects_batch_id_67b3e4b1;
DROP INDEX IF EXISTS public.project_recycle_bin_restored_by_id_2665a121;
DROP INDEX IF EXISTS public.project_recycle_bin_project_id_b9c359f1;
DROP INDEX IF EXISTS public.project_recycle_bin_deleted_by_id_5d1409f9;
DROP INDEX IF EXISTS public.project_push_records_project_id_9dd8de15;
DROP INDEX IF EXISTS public.project_progress_project_id_c9b0d403;
DROP INDEX IF EXISTS public.project_progress_created_by_id_bfa96ce7;
DROP INDEX IF EXISTS public.project_phase_instances_project_id_9f3b1467;
DROP INDEX IF EXISTS public.project_phase_instances_created_by_id_7783b14c;
DROP INDEX IF EXISTS public.project_members_user_id_2e9d44b1;
DROP INDEX IF EXISTS public.project_members_project_id_bf2e42ec;
DROP INDEX IF EXISTS public.project_expenditures_project_id_6c79dd16;
DROP INDEX IF EXISTS public.project_expenditures_created_by_id_283ff779;
DROP INDEX IF EXISTS public.project_expenditures_category_id_b5d751a0;
DROP INDEX IF EXISTS public.project_exp_project_fcb7bd_idx;
DROP INDEX IF EXISTS public.project_change_reviews_reviewer_id_3abd4640;
DROP INDEX IF EXISTS public.project_change_reviews_change_request_id_7de00e2e;
DROP INDEX IF EXISTS public.project_change_requests_project_id_3231f0af;
DROP INDEX IF EXISTS public.project_change_requests_created_by_id_58f7c62d;
DROP INDEX IF EXISTS public.project_batches_code_560841e3_like;
DROP INDEX IF EXISTS public.project_advisors_user_id_e397bc74;
DROP INDEX IF EXISTS public.project_advisors_project_id_d2ef5924;
DROP INDEX IF EXISTS public.project_achievements_project_id_99c3182e;
DROP INDEX IF EXISTS public.project_achievements_achievement_type_id_1d76d968;
DROP INDEX IF EXISTS public.project_ach_project_5cdff8_idx;
DROP INDEX IF EXISTS public.notifications_related_project_id_937ebb75;
DROP INDEX IF EXISTS public.notifications_recipient_id_e1133bac;
DROP INDEX IF EXISTS public.notificatio_recipie_583549_idx;
DROP INDEX IF EXISTS public.login_logs_user_id_d31d00a1;
DROP INDEX IF EXISTS public.expert_groups_members_user_id_94d717a7;
DROP INDEX IF EXISTS public.expert_groups_members_expertgroup_id_c0b06855;
DROP INDEX IF EXISTS public.expert_groups_created_by_id_ea191c03;
DROP INDEX IF EXISTS public.django_session_session_key_c0390e0f_like;
DROP INDEX IF EXISTS public.django_session_expire_date_a5c62663;
DROP INDEX IF EXISTS public.django_admin_log_user_id_c564eba6;
DROP INDEX IF EXISTS public.django_admin_log_content_type_id_c4bce8eb;
DROP INDEX IF EXISTS public.dictionary_types_code_0d0f74a4_like;
DROP INDEX IF EXISTS public.dictionary_items_value_cc3d1c81_like;
DROP INDEX IF EXISTS public.dictionary_items_value_cc3d1c81;
DROP INDEX IF EXISTS public.dictionary_items_dict_type_id_08d3c96f;
DROP INDEX IF EXISTS public.dictionary__dict_ty_efa91e_idx;
DROP INDEX IF EXISTS public.certificate_settings_updated_by_id_2d83e676;
DROP INDEX IF EXISTS public.certificate_settings_project_level_id_0ca1dab1;
DROP INDEX IF EXISTS public.certificate_settings_project_category_id_eb459b98;
DROP INDEX IF EXISTS public.auth_permission_content_type_id_2f476e4b;
DROP INDEX IF EXISTS public.auth_group_permissions_permission_id_84c5c92e;
DROP INDEX IF EXISTS public.auth_group_permissions_group_id_b120cbf9;
DROP INDEX IF EXISTS public.auth_group_name_a6ea08ec_like;
ALTER TABLE IF EXISTS ONLY public.workflow_nodes DROP CONSTRAINT IF EXISTS workflow_nodes_workflow_id_code_63ae61b1_uniq;
ALTER TABLE IF EXISTS ONLY public.workflow_nodes DROP CONSTRAINT IF EXISTS workflow_nodes_pkey;
ALTER TABLE IF EXISTS ONLY public.workflow_configs DROP CONSTRAINT IF EXISTS workflow_configs_pkey;
ALTER TABLE IF EXISTS ONLY public.workflow_configs DROP CONSTRAINT IF EXISTS workflow_configs_phase_batch_id_version_06d76f32_uniq;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_username_key;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_user_id_permission_id_3b86cbdf_uniq;
ALTER TABLE IF EXISTS ONLY public.users_user_permissions DROP CONSTRAINT IF EXISTS users_user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_user_id_group_id_fc7788e8_uniq;
ALTER TABLE IF EXISTS ONLY public.users_groups DROP CONSTRAINT IF EXISTS users_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_employee_id_key;
ALTER TABLE IF EXISTS ONLY public.project_phase_instances DROP CONSTRAINT IF EXISTS uniq_project_phase_attempt;
ALTER TABLE IF EXISTS ONLY public.system_settings DROP CONSTRAINT IF EXISTS system_settings_pkey;
ALTER TABLE IF EXISTS ONLY public.system_settings DROP CONSTRAINT IF EXISTS system_settings_code_batch_id_9901544a_uniq;
ALTER TABLE IF EXISTS ONLY public.reviews DROP CONSTRAINT IF EXISTS reviews_pkey;
ALTER TABLE IF EXISTS ONLY public.review_templates DROP CONSTRAINT IF EXISTS review_templates_pkey;
ALTER TABLE IF EXISTS ONLY public.review_template_items DROP CONSTRAINT IF EXISTS review_template_items_pkey;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_project_no_key;
ALTER TABLE IF EXISTS ONLY public.projects DROP CONSTRAINT IF EXISTS projects_pkey;
ALTER TABLE IF EXISTS ONLY public.project_recycle_bin DROP CONSTRAINT IF EXISTS project_recycle_bin_pkey;
ALTER TABLE IF EXISTS ONLY public.project_push_records DROP CONSTRAINT IF EXISTS project_push_records_pkey;
ALTER TABLE IF EXISTS ONLY public.project_progress DROP CONSTRAINT IF EXISTS project_progress_pkey;
ALTER TABLE IF EXISTS ONLY public.project_phase_instances DROP CONSTRAINT IF EXISTS project_phase_instances_pkey;
ALTER TABLE IF EXISTS ONLY public.project_members DROP CONSTRAINT IF EXISTS project_members_project_id_user_id_ab18bfcc_uniq;
ALTER TABLE IF EXISTS ONLY public.project_members DROP CONSTRAINT IF EXISTS project_members_pkey;
ALTER TABLE IF EXISTS ONLY public.project_expenditures DROP CONSTRAINT IF EXISTS project_expenditures_pkey;
ALTER TABLE IF EXISTS ONLY public.project_change_reviews DROP CONSTRAINT IF EXISTS project_change_reviews_pkey;
ALTER TABLE IF EXISTS ONLY public.project_change_requests DROP CONSTRAINT IF EXISTS project_change_requests_pkey;
ALTER TABLE IF EXISTS ONLY public.project_batches DROP CONSTRAINT IF EXISTS project_batches_pkey;
ALTER TABLE IF EXISTS ONLY public.project_batches DROP CONSTRAINT IF EXISTS project_batches_code_key;
ALTER TABLE IF EXISTS ONLY public.project_archives DROP CONSTRAINT IF EXISTS project_archives_project_id_key;
ALTER TABLE IF EXISTS ONLY public.project_archives DROP CONSTRAINT IF EXISTS project_archives_pkey;
ALTER TABLE IF EXISTS ONLY public.project_advisors DROP CONSTRAINT IF EXISTS project_advisors_pkey;
ALTER TABLE IF EXISTS ONLY public.project_achievements DROP CONSTRAINT IF EXISTS project_achievements_pkey;
ALTER TABLE IF EXISTS ONLY public.notifications DROP CONSTRAINT IF EXISTS notifications_pkey;
ALTER TABLE IF EXISTS ONLY public.login_logs DROP CONSTRAINT IF EXISTS login_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.expert_groups DROP CONSTRAINT IF EXISTS expert_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.expert_groups_members DROP CONSTRAINT IF EXISTS expert_groups_members_pkey;
ALTER TABLE IF EXISTS ONLY public.expert_groups_members DROP CONSTRAINT IF EXISTS expert_groups_members_expertgroup_id_user_id_abc88dfa_uniq;
ALTER TABLE IF EXISTS ONLY public.django_session DROP CONSTRAINT IF EXISTS django_session_pkey;
ALTER TABLE IF EXISTS ONLY public.django_migrations DROP CONSTRAINT IF EXISTS django_migrations_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_pkey;
ALTER TABLE IF EXISTS ONLY public.django_content_type DROP CONSTRAINT IF EXISTS django_content_type_app_label_model_76bd3d3b_uniq;
ALTER TABLE IF EXISTS ONLY public.django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_pkey;
ALTER TABLE IF EXISTS ONLY public.dictionary_types DROP CONSTRAINT IF EXISTS dictionary_types_pkey;
ALTER TABLE IF EXISTS ONLY public.dictionary_types DROP CONSTRAINT IF EXISTS dictionary_types_code_key;
ALTER TABLE IF EXISTS ONLY public.dictionary_items DROP CONSTRAINT IF EXISTS dictionary_items_pkey;
ALTER TABLE IF EXISTS ONLY public.dictionary_items DROP CONSTRAINT IF EXISTS dictionary_items_dict_type_id_value_d443096c_uniq;
ALTER TABLE IF EXISTS ONLY public.certificate_settings DROP CONSTRAINT IF EXISTS certificate_settings_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_permission DROP CONSTRAINT IF EXISTS auth_permission_content_type_id_codename_01ab375a_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.auth_group_permissions DROP CONSTRAINT IF EXISTS auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
ALTER TABLE IF EXISTS ONLY public.auth_group DROP CONSTRAINT IF EXISTS auth_group_name_key;
DROP TABLE IF EXISTS public.workflow_nodes;
DROP TABLE IF EXISTS public.workflow_configs;
DROP TABLE IF EXISTS public.users_user_permissions;
DROP TABLE IF EXISTS public.users_groups;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.system_settings;
DROP TABLE IF EXISTS public.reviews;
DROP TABLE IF EXISTS public.review_templates;
DROP TABLE IF EXISTS public.review_template_items;
DROP TABLE IF EXISTS public.projects;
DROP TABLE IF EXISTS public.project_recycle_bin;
DROP TABLE IF EXISTS public.project_push_records;
DROP TABLE IF EXISTS public.project_progress;
DROP TABLE IF EXISTS public.project_phase_instances;
DROP TABLE IF EXISTS public.project_members;
DROP TABLE IF EXISTS public.project_expenditures;
DROP TABLE IF EXISTS public.project_change_reviews;
DROP TABLE IF EXISTS public.project_change_requests;
DROP TABLE IF EXISTS public.project_batches;
DROP TABLE IF EXISTS public.project_archives;
DROP TABLE IF EXISTS public.project_advisors;
DROP TABLE IF EXISTS public.project_achievements;
DROP TABLE IF EXISTS public.notifications;
DROP TABLE IF EXISTS public.login_logs;
DROP TABLE IF EXISTS public.expert_groups_members;
DROP TABLE IF EXISTS public.expert_groups;
DROP TABLE IF EXISTS public.django_session;
DROP TABLE IF EXISTS public.django_migrations;
DROP TABLE IF EXISTS public.django_content_type;
DROP TABLE IF EXISTS public.django_admin_log;
DROP TABLE IF EXISTS public.dictionary_types;
DROP TABLE IF EXISTS public.dictionary_items;
DROP TABLE IF EXISTS public.certificate_settings;
DROP TABLE IF EXISTS public.auth_permission;
DROP TABLE IF EXISTS public.auth_group_permissions;
DROP TABLE IF EXISTS public.auth_group;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: certificate_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.certificate_settings (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    school_name character varying(100) NOT NULL,
    issuer_name character varying(100) NOT NULL,
    template_code character varying(50) NOT NULL,
    background_image character varying(100),
    seal_image character varying(100),
    style_config jsonb NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    project_category_id bigint,
    project_level_id bigint,
    updated_by_id bigint
);


--
-- Name: certificate_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.certificate_settings ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.certificate_settings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dictionary_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dictionary_items (
    id bigint NOT NULL,
    value character varying(50) NOT NULL,
    label character varying(100) NOT NULL,
    sort_order integer NOT NULL,
    is_active boolean NOT NULL,
    extra_data jsonb,
    description character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    dict_type_id bigint NOT NULL,
    template_file character varying(100)
);


--
-- Name: dictionary_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.dictionary_items ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.dictionary_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dictionary_types; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dictionary_types (
    id bigint NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    description text NOT NULL,
    is_system boolean NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
);


--
-- Name: dictionary_types_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.dictionary_types ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.dictionary_types_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id bigint NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: expert_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expert_groups (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    created_by_id bigint NOT NULL,
    scope character varying(20) NOT NULL
);


--
-- Name: expert_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.expert_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.expert_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: expert_groups_members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.expert_groups_members (
    id bigint NOT NULL,
    expertgroup_id bigint NOT NULL,
    user_id bigint NOT NULL
);


--
-- Name: expert_groups_members_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.expert_groups_members ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.expert_groups_members_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: login_logs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.login_logs (
    id bigint NOT NULL,
    login_time timestamp with time zone NOT NULL,
    ip_address inet NOT NULL,
    user_agent character varying(200) NOT NULL,
    login_status boolean NOT NULL,
    user_id bigint NOT NULL
);


--
-- Name: login_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.login_logs ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.login_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id bigint NOT NULL,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    notification_type character varying(20) NOT NULL,
    is_read boolean NOT NULL,
    read_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    recipient_id bigint NOT NULL,
    related_project_id bigint
);


--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.notifications ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.notifications_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_achievements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_achievements (
    id bigint NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    authors character varying(200) NOT NULL,
    journal character varying(200) NOT NULL,
    publication_date date,
    doi character varying(100) NOT NULL,
    patent_no character varying(100) NOT NULL,
    patent_type character varying(50) NOT NULL,
    applicant character varying(200) NOT NULL,
    copyright_no character varying(100) NOT NULL,
    copyright_owner character varying(200) NOT NULL,
    competition_name character varying(200) NOT NULL,
    award_level character varying(50) NOT NULL,
    award_date date,
    attachment character varying(255),
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    achievement_type_id bigint NOT NULL,
    project_id bigint NOT NULL,
    extra_data jsonb NOT NULL
);


--
-- Name: project_achievements_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_achievements ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_achievements_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_advisors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_advisors (
    id bigint NOT NULL,
    "order" integer NOT NULL,
    project_id bigint NOT NULL,
    user_id bigint NOT NULL
);


--
-- Name: project_advisors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_advisors ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_advisors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_archives; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_archives (
    id bigint NOT NULL,
    snapshot jsonb NOT NULL,
    attachments jsonb NOT NULL,
    archived_at timestamp with time zone NOT NULL,
    project_id bigint NOT NULL
);


--
-- Name: project_archives_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_archives ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_archives_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_batches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_batches (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    year integer NOT NULL,
    code character varying(50) NOT NULL,
    is_current boolean NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    status character varying(20) NOT NULL,
    is_deleted boolean NOT NULL
);


--
-- Name: project_batches_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_batches ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_batches_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_change_requests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_change_requests (
    id bigint NOT NULL,
    request_type character varying(20) NOT NULL,
    reason text NOT NULL,
    change_data jsonb,
    requested_end_date date,
    attachment character varying(255),
    status character varying(30) NOT NULL,
    submitted_at timestamp with time zone,
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    created_by_id bigint NOT NULL,
    project_id bigint NOT NULL
);


--
-- Name: project_change_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_change_requests ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_change_requests_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_change_reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_change_reviews (
    id bigint NOT NULL,
    review_level character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    comments text NOT NULL,
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    change_request_id bigint NOT NULL,
    reviewer_id bigint
);


--
-- Name: project_change_reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_change_reviews ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_change_reviews_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_expenditures; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_expenditures (
    id bigint NOT NULL,
    title character varying(200) NOT NULL,
    amount numeric(10,2) NOT NULL,
    expenditure_date date NOT NULL,
    proof_file character varying(255),
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    category_id bigint NOT NULL,
    created_by_id bigint NOT NULL,
    project_id bigint NOT NULL
);


--
-- Name: project_expenditures_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_expenditures ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_expenditures_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_members (
    id bigint NOT NULL,
    role character varying(20) NOT NULL,
    join_date date NOT NULL,
    contribution text NOT NULL,
    project_id bigint NOT NULL,
    user_id bigint NOT NULL
);


--
-- Name: project_members_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_members ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_members_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_phase_instances; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_phase_instances (
    id bigint NOT NULL,
    phase character varying(20) NOT NULL,
    attempt_no integer NOT NULL,
    step character varying(50) NOT NULL,
    state character varying(20) NOT NULL,
    return_to character varying(20) NOT NULL,
    returned_reason text NOT NULL,
    returned_at timestamp with time zone,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    created_by_id bigint,
    project_id bigint NOT NULL,
    CONSTRAINT project_phase_instances_attempt_no_check CHECK ((attempt_no >= 0))
);


--
-- Name: project_phase_instances_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_phase_instances ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_phase_instances_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_progress; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_progress (
    id bigint NOT NULL,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    attachment character varying(255),
    created_at timestamp with time zone NOT NULL,
    created_by_id bigint NOT NULL,
    project_id bigint NOT NULL
);


--
-- Name: project_progress_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_progress ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_progress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_push_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_push_records (
    id bigint NOT NULL,
    target character varying(100) NOT NULL,
    payload jsonb NOT NULL,
    response_message text NOT NULL,
    status character varying(20) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    project_id bigint NOT NULL
);


--
-- Name: project_push_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_push_records ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_push_records_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: project_recycle_bin; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.project_recycle_bin (
    id bigint NOT NULL,
    resource_type character varying(20) NOT NULL,
    resource_id integer,
    payload jsonb NOT NULL,
    attachments jsonb NOT NULL,
    deleted_at timestamp with time zone NOT NULL,
    restored_at timestamp with time zone,
    is_restored boolean NOT NULL,
    deleted_by_id bigint,
    project_id bigint NOT NULL,
    restored_by_id bigint
);


--
-- Name: project_recycle_bin_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.project_recycle_bin ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.project_recycle_bin_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.projects (
    id bigint NOT NULL,
    project_no character varying(50) NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    is_key_field boolean NOT NULL,
    self_funding numeric(10,2) NOT NULL,
    category_description text NOT NULL,
    start_date date,
    end_date date,
    budget numeric(10,2) NOT NULL,
    research_content text NOT NULL,
    research_plan text NOT NULL,
    expected_results text NOT NULL,
    innovation_points text NOT NULL,
    proposal_file character varying(255),
    attachment_file character varying(255),
    final_report character varying(255),
    achievement_file character varying(255),
    status character varying(30) NOT NULL,
    ranking integer,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    submitted_at timestamp with time zone,
    closure_applied_at timestamp with time zone,
    category_id bigint,
    leader_id bigint NOT NULL,
    level_id bigint,
    source_id bigint,
    year integer NOT NULL,
    key_domain_code character varying(50) NOT NULL,
    mid_term_report character varying(255),
    mid_term_submitted_at timestamp with time zone,
    approved_budget numeric(10,2),
    batch_id bigint,
    contract_file character varying(255),
    task_book_file character varying(255),
    expected_results_data jsonb NOT NULL,
    achievement_summary text NOT NULL,
    discipline_id bigint
);


--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.projects ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.projects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: review_template_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.review_template_items (
    id bigint NOT NULL,
    title character varying(200) NOT NULL,
    description text NOT NULL,
    weight numeric(5,2) NOT NULL,
    max_score integer NOT NULL,
    is_required boolean NOT NULL,
    sort_order integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    template_id bigint NOT NULL
);


--
-- Name: review_template_items_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.review_template_items ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.review_template_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: review_templates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.review_templates (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    review_type character varying(20) NOT NULL,
    review_level character varying(20) NOT NULL,
    scope character varying(20) NOT NULL,
    description text NOT NULL,
    notice text NOT NULL,
    is_active boolean NOT NULL,
    is_locked boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    batch_id bigint,
    created_by_id bigint,
    updated_by_id bigint
);


--
-- Name: review_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.review_templates ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.review_templates_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reviews (
    id bigint NOT NULL,
    review_type character varying(20) NOT NULL,
    review_level character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    comments text NOT NULL,
    score integer,
    closure_rating character varying(20),
    created_at timestamp with time zone NOT NULL,
    reviewed_at timestamp with time zone,
    project_id bigint NOT NULL,
    reviewer_id bigint,
    phase_instance_id bigint,
    score_details jsonb NOT NULL,
    review_template_id bigint
);


--
-- Name: reviews_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.reviews ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.reviews_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_settings (
    id bigint NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    data jsonb NOT NULL,
    is_locked boolean NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    updated_by_id bigint,
    batch_id bigint
);


--
-- Name: system_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.system_settings ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.system_settings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    is_staff boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL,
    role character varying(20) NOT NULL,
    employee_id character varying(20) NOT NULL,
    real_name character varying(50) NOT NULL,
    phone character varying(11) NOT NULL,
    email character varying(254) NOT NULL,
    major character varying(100) NOT NULL,
    grade character varying(10) NOT NULL,
    class_name character varying(50) NOT NULL,
    college character varying(100) NOT NULL,
    department character varying(100) NOT NULL,
    avatar character varying(100),
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    title character varying(50) NOT NULL,
    expert_scope character varying(20) NOT NULL
);


--
-- Name: users_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users_groups (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: users_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: users_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users_user_permissions (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: users_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.users_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.users_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: workflow_configs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workflow_configs (
    id bigint NOT NULL,
    name character varying(100) NOT NULL,
    phase character varying(20) NOT NULL,
    version integer NOT NULL,
    description text NOT NULL,
    is_active boolean NOT NULL,
    is_locked boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    batch_id bigint,
    created_by_id bigint,
    updated_by_id bigint
);


--
-- Name: workflow_configs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.workflow_configs ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.workflow_configs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: workflow_nodes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workflow_nodes (
    id bigint NOT NULL,
    code character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    node_type character varying(20) NOT NULL,
    role character varying(20) NOT NULL,
    review_level character varying(20) NOT NULL,
    scope character varying(20) NOT NULL,
    return_policy character varying(20) NOT NULL,
    notice text NOT NULL,
    sort_order integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    review_template_id bigint,
    workflow_id bigint NOT NULL
);


--
-- Name: workflow_nodes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.workflow_nodes ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.workflow_nodes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	3	add_permission
6	Can change permission	3	change_permission
7	Can delete permission	3	delete_permission
8	Can view permission	3	view_permission
9	Can add group	2	add_group
10	Can change group	2	change_group
11	Can delete group	2	delete_group
12	Can view group	2	view_group
13	Can add content type	4	add_contenttype
14	Can change content type	4	change_contenttype
15	Can delete content type	4	delete_contenttype
16	Can view content type	4	view_contenttype
17	Can add session	5	add_session
18	Can change session	5	change_session
19	Can delete session	5	delete_session
20	Can view session	5	view_session
21	Can add 用户	7	add_user
22	Can change 用户	7	change_user
23	Can delete 用户	7	delete_user
24	Can view 用户	7	view_user
25	Can add 登录日志	6	add_loginlog
26	Can change 登录日志	6	change_loginlog
27	Can delete 登录日志	6	delete_loginlog
28	Can view 登录日志	6	view_loginlog
29	Can add 项目成果	9	add_projectachievement
30	Can change 项目成果	9	change_projectachievement
31	Can delete 项目成果	9	delete_projectachievement
32	Can view 项目成果	9	view_projectachievement
33	Can add 项目指导教师	10	add_projectadvisor
34	Can change 项目指导教师	10	change_projectadvisor
35	Can delete 项目指导教师	10	delete_projectadvisor
36	Can view 项目指导教师	10	view_projectadvisor
37	Can add 项目成员	11	add_projectmember
38	Can change 项目成员	11	change_projectmember
39	Can delete 项目成员	11	delete_projectmember
40	Can view 项目成员	11	view_projectmember
41	Can add 项目进度	12	add_projectprogress
42	Can change 项目进度	12	change_projectprogress
43	Can delete 项目进度	12	delete_projectprogress
44	Can view 项目进度	12	view_projectprogress
45	Can add 项目	8	add_project
46	Can change 项目	8	change_project
47	Can delete 项目	8	delete_project
48	Can view 项目	8	view_project
49	Can add 审核记录	13	add_review
50	Can change 审核记录	13	change_review
51	Can delete 审核记录	13	delete_review
52	Can view 审核记录	13	view_review
53	Can add 通知	14	add_notification
54	Can change 通知	14	change_notification
55	Can delete 通知	14	delete_notification
56	Can view 通知	14	view_notification
57	Can add 字典类型	16	add_dictionarytype
58	Can change 字典类型	16	change_dictionarytype
59	Can delete 字典类型	16	delete_dictionarytype
60	Can view 字典类型	16	view_dictionarytype
61	Can add 字典条目	15	add_dictionaryitem
62	Can change 字典条目	15	change_dictionaryitem
63	Can delete 字典条目	15	delete_dictionaryitem
64	Can view 字典条目	15	view_dictionaryitem
65	Can add 经费支出	17	add_projectexpenditure
66	Can change 经费支出	17	change_projectexpenditure
67	Can delete 经费支出	17	delete_projectexpenditure
68	Can view 经费支出	17	view_projectexpenditure
69	Can add 专家组	18	add_expertgroup
70	Can change 专家组	18	change_expertgroup
71	Can delete 专家组	18	delete_expertgroup
72	Can view 专家组	18	view_expertgroup
73	Can add 结题证书配置	19	add_certificatesetting
74	Can change 结题证书配置	19	change_certificatesetting
75	Can delete 结题证书配置	19	delete_certificatesetting
76	Can view 结题证书配置	19	view_certificatesetting
77	Can add 系统配置	20	add_systemsetting
78	Can change 系统配置	20	change_systemsetting
79	Can delete 系统配置	20	delete_systemsetting
80	Can view 系统配置	20	view_systemsetting
81	Can add 项目变更申请	21	add_projectchangerequest
82	Can change 项目变更申请	21	change_projectchangerequest
83	Can delete 项目变更申请	21	delete_projectchangerequest
84	Can view 项目变更申请	21	view_projectchangerequest
85	Can add 项目变更审核	22	add_projectchangereview
86	Can change 项目变更审核	22	change_projectchangereview
87	Can delete 项目变更审核	22	delete_projectchangereview
88	Can view 项目变更审核	22	view_projectchangereview
89	Can add 项目推送记录	24	add_projectpushrecord
90	Can change 项目推送记录	24	change_projectpushrecord
91	Can delete 项目推送记录	24	delete_projectpushrecord
92	Can view 项目推送记录	24	view_projectpushrecord
93	Can add 项目归档	23	add_projectarchive
94	Can change 项目归档	23	change_projectarchive
95	Can delete 项目归档	23	delete_projectarchive
96	Can view 项目归档	23	view_projectarchive
97	Can add 项目批次	25	add_projectbatch
98	Can change 项目批次	25	change_projectbatch
99	Can delete 项目批次	25	delete_projectbatch
100	Can view 项目批次	25	view_projectbatch
101	Can add 项目阶段实例	26	add_projectphaseinstance
102	Can change 项目阶段实例	26	change_projectphaseinstance
103	Can delete 项目阶段实例	26	delete_projectphaseinstance
104	Can view 项目阶段实例	26	view_projectphaseinstance
105	Can add 项目回收站	27	add_projectrecyclebin
106	Can change 项目回收站	27	change_projectrecyclebin
107	Can delete 项目回收站	27	delete_projectrecyclebin
108	Can view 项目回收站	27	view_projectrecyclebin
109	Can add 流程配置	30	add_workflowconfig
110	Can change 流程配置	30	change_workflowconfig
111	Can delete 流程配置	30	delete_workflowconfig
112	Can view 流程配置	30	view_workflowconfig
113	Can add 评审模板	28	add_reviewtemplate
114	Can change 评审模板	28	change_reviewtemplate
115	Can delete 评审模板	28	delete_reviewtemplate
116	Can view 评审模板	28	view_reviewtemplate
117	Can add 评审模板评分项	29	add_reviewtemplateitem
118	Can change 评审模板评分项	29	change_reviewtemplateitem
119	Can delete 评审模板评分项	29	delete_reviewtemplateitem
120	Can view 评审模板评分项	29	view_reviewtemplateitem
121	Can add 流程节点	31	add_workflownode
122	Can change 流程节点	31	change_workflownode
123	Can delete 流程节点	31	delete_workflownode
124	Can view 流程节点	31	view_workflownode
\.


--
-- Data for Name: certificate_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.certificate_settings (id, name, school_name, issuer_name, template_code, background_image, seal_image, style_config, is_active, created_at, updated_at, project_category_id, project_level_id, updated_by_id) FROM stdin;
\.


--
-- Data for Name: dictionary_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dictionary_items (id, value, label, sort_order, is_active, extra_data, description, created_at, updated_at, dict_type_id, template_file) FROM stdin;
1	TEACHER_RESEARCH	面向教师科研类	1	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	1	\N
13	METALLURGY	冶金工程学院	1	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	5	\N
14	MATERIALS	材料科学与工程学院	2	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	5	\N
15	CHEMISTRY	化学与化工学院	3	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	5	\N
16	CIVIL_ENG	建筑工程学院	4	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	5	\N
17	MECHANICAL	机械工程学院	5	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	5	\N
18	ELECTRICAL	电气与信息工程学院	6	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	5	\N
19	CS	计算机科学与技术学院	7	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	5	\N
20	PHILOSOPHY	哲学类	1	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	6	\N
21	ECONOMICS	经济学类	2	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	6	\N
22	FINANCE	财政学类	3	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	6	\N
23	BANKING	金融学类	4	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	6	\N
24	TRADE	经济与贸易类	5	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	6	\N
25	LAW	法学类	6	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	6	\N
26	POLITICS	政治学类	7	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08	6	\N
27	PROFESSOR	教授	1	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 23:43:15.694567+08	10	\N
28	ASSOCIATE_PROFESSOR	副教授	2	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 23:43:15.696779+08	10	\N
29	SENIOR_LAB_TECHNICIAN	高级实验师	3	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 23:43:15.697608+08	10	\N
30	LECTURER	讲师(高校)	4	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 23:43:15.698461+08	10	\N
31	ASSISTANT	助教(高校)	5	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 23:43:15.699188+08	10	\N
32	ASSISTANT_LAB_TECHNICIAN	助理实验师	6	t	\N		2025-12-16 17:16:42.577506+08	2025-12-16 23:43:15.700015+08	10	\N
37	研究员	研究员	7	t	\N		2025-12-16 23:14:22.736183+08	2025-12-16 23:43:15.700691+08	10	\N
8	创新训练项目	创新训练项目	1	t	{}		2025-12-16 17:16:42.577506+08	2025-12-17 00:47:12.829205+08	9	dictionary_templates/附件1安徽工业大学大学生创新训练项目申报书.doc
10	创业实践项目	创业实践项目	3	t	{}		2025-12-16 17:16:42.577506+08	2025-12-17 00:47:27.823459+08	9	dictionary_templates/2021安徽工业大学大学生创业实践项目申报书.doc
38	202406	测试	1	t	{}		2025-12-17 11:43:54.117801+08	2025-12-17 11:43:54.117821+08	13	
39	0804	材料类	8	t	{}		2025-12-17 11:49:50.616269+08	2025-12-17 11:49:50.616279+08	6	
44	ENTREPRENEURSHIP_TRAINING	创业训练项目	2	t	\N		2025-12-17 12:15:45.713708+08	2025-12-17 12:31:05.051555+08	9	
54	省级	省级	2	t	{"budget": 3000}		2025-12-17 12:42:58.150703+08	2025-12-17 12:44:37.257857+08	2	
55	国家级	国家级	3	t	{"budget": 10000}		2025-12-17 12:42:58.151891+08	2025-12-17 12:44:44.687174+08	2	
53	校级一般	校级一般	1	t	{"budget": 1000}		2025-12-17 12:42:58.14498+08	2025-12-17 12:44:54.597118+08	2	
56	校级重点	校级重点	4	t	{"budget": 3000}		2025-12-17 12:45:04.632778+08	2025-12-17 12:45:04.632785+08	2	
62	学科竞赛类	学科竞赛类	2	t	{}		2025-12-17 13:04:16.484357+08	2025-12-17 13:04:16.484365+08	1	
63	学生自主类	学生自主类	3	t	{}		2025-12-17 13:04:34.247402+08	2025-12-17 13:04:34.247416+08	1	
64	论文	论文	1	t	{}		2025-12-26 22:54:19.169413+08	2025-12-26 22:54:19.169422+08	12	
65	专利	专利	2	t	{}		2025-12-26 22:54:24.807253+08	2025-12-26 22:54:24.807263+08	12	
66	软著	软著	3	t	{}		2025-12-26 22:54:33.57505+08	2025-12-26 22:54:33.575059+08	12	
\.


--
-- Data for Name: dictionary_types; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dictionary_types (id, code, name, description, is_system, is_active, created_at, updated_at) FROM stdin;
1	project_source	项目来源	项目来源分类	f	t	2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08
2	project_level	项目级别	项目级别分类	f	t	2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08
5	college	学院	学校下属学院	f	t	2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08
6	major_category	专业大类	项目所属专业大类	f	t	2025-12-16 17:16:42.577506+08	2025-12-16 17:16:42.577506+08
12	achievement_type	成果类型	项目成果类型，如：论文、专利、软著	t	t	2025-12-16 20:52:43.568287+08	2025-12-16 20:52:43.568291+08
13	key_field_code	重点领域	Key field codes	t	t	2025-12-16 21:26:25.85553+08	2025-12-16 21:26:25.855539+08
9	project_type	项目类别	项目类型，如：A类、B类	t	t	2025-12-16 20:52:43.563065+08	2025-12-16 20:52:43.563071+08
10	title	教师职称	教师职称，如：教授、副教授、讲师	t	t	2025-12-16 20:52:43.564943+08	2025-12-16 20:52:43.564948+08
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	group
3	auth	permission
4	contenttypes	contenttype
5	sessions	session
6	users	loginlog
7	users	user
8	projects	project
9	projects	projectachievement
10	projects	projectadvisor
11	projects	projectmember
12	projects	projectprogress
13	reviews	review
14	notifications	notification
15	dictionaries	dictionaryitem
16	dictionaries	dictionarytype
17	projects	projectexpenditure
18	reviews	expertgroup
19	system_settings	certificatesetting
20	system_settings	systemsetting
21	projects	projectchangerequest
22	projects	projectchangereview
23	projects	projectarchive
24	projects	projectpushrecord
25	system_settings	projectbatch
26	projects	projectphaseinstance
27	projects	projectrecyclebin
28	system_settings	reviewtemplate
29	system_settings	reviewtemplateitem
30	system_settings	workflowconfig
31	system_settings	workflownode
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2025-12-16 17:11:17.061848+08
2	contenttypes	0002_remove_content_type_name	2025-12-16 17:11:17.066218+08
3	auth	0001_initial	2025-12-16 17:11:17.104008+08
4	auth	0002_alter_permission_name_max_length	2025-12-16 17:11:17.108905+08
5	auth	0003_alter_user_email_max_length	2025-12-16 17:11:17.112349+08
6	auth	0004_alter_user_username_opts	2025-12-16 17:11:17.115943+08
7	auth	0005_alter_user_last_login_null	2025-12-16 17:11:17.11974+08
8	auth	0006_require_contenttypes_0002	2025-12-16 17:11:17.121725+08
9	auth	0007_alter_validators_add_error_messages	2025-12-16 17:11:17.126355+08
10	auth	0008_alter_user_username_max_length	2025-12-16 17:11:17.130694+08
11	auth	0009_alter_user_last_name_max_length	2025-12-16 17:11:17.134522+08
12	auth	0010_alter_group_name_max_length	2025-12-16 17:11:17.140998+08
13	auth	0011_update_proxy_permissions	2025-12-16 17:11:17.146265+08
14	auth	0012_alter_user_first_name_max_length	2025-12-16 17:11:17.15138+08
15	users	0001_initial	2025-12-16 17:11:17.218915+08
16	admin	0001_initial	2025-12-16 17:11:17.235222+08
17	admin	0002_logentry_remove_auto_add	2025-12-16 17:11:17.239957+08
18	admin	0003_logentry_add_action_flag_choices	2025-12-16 17:11:17.246328+08
19	dictionaries	0001_initial	2025-12-16 17:11:17.28314+08
20	projects	0001_initial	2025-12-16 17:11:17.320386+08
21	notifications	0001_initial	2025-12-16 17:11:17.3284+08
22	notifications	0002_initial	2025-12-16 17:11:17.364073+08
23	projects	0002_initial	2025-12-16 17:11:17.535852+08
24	reviews	0001_initial	2025-12-16 17:11:17.552791+08
25	reviews	0002_initial	2025-12-16 17:11:17.594545+08
26	sessions	0001_initial	2025-12-16 17:11:17.604717+08
27	dictionaries	0002_seed_initial_dictionaries	2025-12-16 21:26:25.865724+08
28	dictionaries	0003_dictionaryitem_template_file	2025-12-17 00:45:48.103459+08
29	users	0002_user_title_alter_user_role	2025-12-17 01:07:20.4652+08
30	projects	0003_project_year	2025-12-17 12:07:46.720509+08
31	dictionaries	0004_seed_project_level_items	2025-12-17 12:53:47.362542+08
32	projects	0004_project_key_domain_code	2025-12-17 13:58:43.243283+08
33	projects	0005_project_mid_term_report_and_more	2025-12-23 13:52:29.534785+08
34	reviews	0003_alter_review_review_type	2025-12-23 13:52:29.54517+08
35	projects	0006_projectexpenditure	2025-12-23 13:57:34.099341+08
36	reviews	0004_expertgroup	2025-12-23 14:09:05.812507+08
37	users	0003_alter_user_role	2025-12-23 14:09:05.824648+08
38	reviews	0005_expertgroup_scope_alter_review_review_level	2025-12-23 15:05:19.897899+08
39	projects	0007_alter_project_status	2025-12-23 15:09:55.725832+08
40	projects	0008_project_approved_budget	2025-12-23 16:04:52.17221+08
41	system_settings	0001_initial	2025-12-23 16:48:55.102538+08
42	projects	0009_project_change_requests	2025-12-23 17:01:48.600511+08
43	projects	0010_project_status_terminated	2025-12-23 17:01:48.612169+08
44	projects	0011_project_archive_push	2025-12-23 17:09:16.256865+08
45	users	0004_user_expert_scope	2025-12-24 14:48:43.156412+08
46	system_settings	0002_project_batch_and_settings_batch	2025-12-24 15:18:08.722784+08
47	projects	0012_project_batch	2025-12-24 15:18:08.737899+08
48	projects	0013_project_contract_task_book	2025-12-24 16:26:32.107719+08
49	projects	0014_project_expected_results_and_achievement_extra	2025-12-24 16:26:32.133178+08
50	system_settings	0003_projectbatch_status	2025-12-26 11:27:30.294693+08
51	system_settings	0004_projectbatch_status_and_level	2025-12-26 15:22:44.077015+08
52	system_settings	0005_alter_projectbatch_id	2025-12-26 16:25:49.82183+08
53	system_settings	0006_remove_projectbatch_project_level	2025-12-26 19:21:02.052718+08
54	system_settings	0007_remove_projectbatch_reviewing	2025-12-26 21:35:32.649166+08
55	projects	0015_project_phase_instance	2025-12-27 12:33:32.712002+08
56	reviews	0006_review_phase_instance	2025-12-27 12:33:32.736003+08
57	projects	0016_alter_project_status	2025-12-27 12:41:02.827672+08
58	projects	0017_project_status_ready_for_closure	2025-12-27 15:50:18.386811+08
59	projects	0018_project_achievement_summary	2025-12-27 16:11:26.163746+08
60	projects	0019_project_recycle_bin	2025-12-27 23:49:35.813385+08
61	projects	0020_project_discipline	2025-12-27 23:49:35.830326+08
62	system_settings	0008_workflow_review_templates	2025-12-27 23:49:35.930352+08
63	reviews	0007_review_template_details	2025-12-27 23:49:35.963333+08
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
\.


--
-- Data for Name: expert_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.expert_groups (id, name, created_at, updated_at, created_by_id, scope) FROM stdin;
1	专家组	2025-12-26 23:46:06.901573+08	2025-12-26 23:46:06.901582+08	21	COLLEGE
2	校级审核	2025-12-27 00:00:31.232211+08	2025-12-27 00:00:31.23222+08	1	SCHOOL
\.


--
-- Data for Name: expert_groups_members; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.expert_groups_members (id, expertgroup_id, user_id) FROM stdin;
1	1	22
2	2	23
\.


--
-- Data for Name: login_logs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.login_logs (id, login_time, ip_address, user_agent, login_status, user_id) FROM stdin;
1	2025-12-16 17:19:49.436992+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
2	2025-12-16 17:21:06.174764+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
4	2025-12-16 18:45:46.34029+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
8	2025-12-16 19:31:38.586652+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
13	2025-12-16 19:36:31.428887+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
29	2025-12-16 20:17:16.676634+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
30	2025-12-16 20:22:00.360907+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
31	2025-12-16 20:22:07.389461+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
32	2025-12-16 20:23:24.335976+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
33	2025-12-16 20:29:34.228623+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
36	2025-12-16 20:38:28.42919+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
41	2025-12-16 22:54:20.01122+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
42	2025-12-16 23:00:51.812341+08	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
45	2025-12-17 10:21:17.995543+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	t	1
51	2025-12-17 14:00:05.925316+08	127.0.0.1	Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0	t	1
52	2025-12-17 14:31:10.591537+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	t	1
54	2025-12-17 14:56:50.411647+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	t	1
60	2025-12-17 16:25:05.066225+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	t	1
63	2025-12-23 14:07:19.109103+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
65	2025-12-23 14:34:00.625131+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
66	2025-12-23 14:59:22.94794+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
67	2025-12-23 15:10:44.343381+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
68	2025-12-23 15:18:56.430977+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
70	2025-12-23 16:49:35.354957+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
74	2025-12-23 20:24:16.352613+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
75	2025-12-23 20:57:26.588574+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
78	2025-12-24 14:18:51.992867+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
79	2025-12-24 14:27:28.846244+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
80	2025-12-24 14:37:30.632413+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
81	2025-12-24 14:49:08.376468+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
82	2025-12-24 14:54:57.199038+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
83	2025-12-26 11:03:04.447593+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
84	2025-12-26 11:06:19.17526+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
85	2025-12-26 11:06:34.780739+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	20
86	2025-12-26 11:06:49.811207+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
87	2025-12-26 11:07:04.262965+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
88	2025-12-26 11:07:19.75145+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	23
89	2025-12-26 11:08:55.322256+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
90	2025-12-26 13:36:53.838653+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
91	2025-12-26 13:55:08.978645+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
92	2025-12-26 13:56:56.217344+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
93	2025-12-26 13:59:16.951768+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	20
94	2025-12-26 14:00:05.867091+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
95	2025-12-26 14:01:06.459565+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
96	2025-12-26 14:23:17.191024+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
97	2025-12-26 14:50:48.933643+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
98	2025-12-26 22:10:58.916657+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
99	2025-12-26 22:22:07.580953+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
100	2025-12-26 22:40:50.235184+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
101	2025-12-26 22:49:27.073939+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
102	2025-12-26 22:54:43.065758+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
103	2025-12-26 23:07:55.920638+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	20
104	2025-12-26 23:15:43.122824+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
105	2025-12-26 23:25:49.367051+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	20
106	2025-12-26 23:26:09.25066+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
107	2025-12-26 23:31:09.94954+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
108	2025-12-26 23:56:38.694971+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
109	2025-12-26 23:57:21.597719+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
110	2025-12-26 23:59:00.934966+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
111	2025-12-26 23:59:38.90401+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
112	2025-12-27 00:04:00.550686+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
113	2025-12-27 00:04:40.11112+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	23
114	2025-12-27 00:05:33.699826+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
115	2025-12-27 00:38:59.039301+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	20
116	2025-12-27 00:39:50.621231+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
117	2025-12-27 00:41:59.973204+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
118	2025-12-27 10:30:53.435663+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
119	2025-12-27 11:26:35.856402+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
120	2025-12-27 11:26:55.971706+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	20
121	2025-12-27 11:27:27.675856+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	23
122	2025-12-27 11:27:40.437582+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
123	2025-12-27 11:28:14.757022+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
124	2025-12-27 11:35:07.930975+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
125	2025-12-27 11:53:17.125342+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
126	2025-12-27 11:55:52.793239+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
127	2025-12-27 12:01:03.013518+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
128	2025-12-27 12:43:36.45652+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
129	2025-12-27 12:44:35.0884+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
130	2025-12-27 12:45:14.921476+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
131	2025-12-27 12:45:46.641328+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	20
132	2025-12-27 12:56:06.176997+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
133	2025-12-27 13:09:47.643516+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
134	2025-12-27 13:11:55.064841+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
135	2025-12-27 13:14:31.985999+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
136	2025-12-27 13:14:59.963049+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
137	2025-12-27 13:21:22.325325+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
138	2025-12-27 15:08:26.254512+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
139	2025-12-27 15:24:23.741557+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
140	2025-12-27 16:13:24.041873+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	20
141	2025-12-27 16:14:39.061517+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
142	2025-12-27 16:33:25.546227+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
143	2025-12-27 16:34:31.563561+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
144	2025-12-27 16:34:43.836821+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	23
145	2025-12-27 16:35:12.056516+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
146	2025-12-27 16:35:33.223741+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
147	2025-12-27 16:43:01.128181+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	20
148	2025-12-27 16:43:21.238283+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
149	2025-12-27 16:43:57.993677+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	22
150	2025-12-27 16:44:18.108588+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
151	2025-12-27 16:44:45.371291+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	21
152	2025-12-27 16:45:08.684466+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
153	2025-12-27 16:46:34.753133+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
154	2025-12-27 16:47:16.829135+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	16
155	2025-12-27 16:49:32.739484+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
156	2025-12-28 16:21:59.14292+08	127.0.0.1	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36	t	1
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications (id, title, content, notification_type, is_read, read_at, created_at, recipient_id, related_project_id) FROM stdin;
1	项目审核未通过	很抱歉，您的项目《镁电解熔盐中杂质的绿色高效分离》审核未通过。\n审核意见：请补充经费预算明细	REVIEW	f	\N	2025-12-26 23:15:04.152215+08	16	4
2	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：同意申报	REVIEW	f	\N	2025-12-26 23:25:54.545234+08	16	4
3	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：院级评审通过	REVIEW	f	\N	2025-12-26 23:58:09.094102+08	16	4
4	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：校级评审通过	REVIEW	f	\N	2025-12-27 00:05:03.415822+08	16	4
5	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：中期导师审核通过	REVIEW	f	\N	2025-12-27 00:39:21.201596+08	16	4
6	项目审核未通过	很抱歉，您的项目《镁电解熔盐中杂质的绿色高效分离》审核未通过。	REVIEW	f	\N	2025-12-27 12:45:02.577892+08	16	4
7	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：通过	REVIEW	f	\N	2025-12-27 12:46:05.258911+08	16	4
8	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：院级中期审核通过	REVIEW	f	\N	2025-12-27 13:12:13.007944+08	16	4
9	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：结题导师审核通过	REVIEW	f	\N	2025-12-27 16:13:39.063182+08	16	4
10	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：123	REVIEW	f	\N	2025-12-27 16:34:59.129884+08	16	4
11	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：90	REVIEW	f	\N	2025-12-27 16:43:06.473937+08	16	4
12	项目审核通过	恭喜！您的项目《镁电解熔盐中杂质的绿色高效分离》审核通过。\n审核意见：0	REVIEW	f	\N	2025-12-27 16:44:08.387967+08	16	4
\.


--
-- Data for Name: project_achievements; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_achievements (id, title, description, authors, journal, publication_date, doi, patent_no, patent_type, applicant, copyright_no, copyright_owner, competition_name, award_level, award_date, attachment, created_at, updated_at, achievement_type_id, project_id, extra_data) FROM stdin;
1	123456				\N									\N	achievements/89d5bca79a244f12aade8b3642a3fa01_PCqAWdK.pdf	2025-12-27 15:52:02.770989+08	2025-12-27 16:42:47.488537+08	64	4	{}
\.


--
-- Data for Name: project_advisors; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_advisors (id, "order", project_id, user_id) FROM stdin;
20	0	4	20
\.


--
-- Data for Name: project_archives; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_archives (id, snapshot, attachments, archived_at, project_id) FROM stdin;
1	{"title": "镁电解熔盐中杂质的绿色高效分离", "leader": 16, "status": "CLOSED", "project_no": "2025METALLURGY0001"}	[]	2025-12-27 16:46:57.108142+08	4
\.


--
-- Data for Name: project_batches; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_batches (id, name, year, code, is_current, is_active, created_at, updated_at, status, is_deleted) FROM stdin;
3	2025第一批	2025	2025A	t	t	2025-12-26 21:38:24.329666+08	2025-12-26 22:07:09.341425+08	active	f
\.


--
-- Data for Name: project_change_requests; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_change_requests (id, request_type, reason, change_data, requested_end_date, attachment, status, submitted_at, reviewed_at, created_at, updated_at, created_by_id, project_id) FROM stdin;
\.


--
-- Data for Name: project_change_reviews; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_change_reviews (id, review_level, status, comments, reviewed_at, created_at, change_request_id, reviewer_id) FROM stdin;
\.


--
-- Data for Name: project_expenditures; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_expenditures (id, title, amount, expenditure_date, proof_file, status, created_at, category_id, created_by_id, project_id) FROM stdin;
\.


--
-- Data for Name: project_members; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_members (id, role, join_date, contribution, project_id, user_id) FROM stdin;
62	MEMBER	2025-12-26		4	17
63	MEMBER	2025-12-26		4	18
64	MEMBER	2025-12-26		4	19
37	LEADER	2025-12-26		4	16
\.


--
-- Data for Name: project_phase_instances; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_phase_instances (id, phase, attempt_no, step, state, return_to, returned_reason, returned_at, created_at, updated_at, created_by_id, project_id) FROM stdin;
1	MID_TERM	1	COMPLETED	COMPLETED			\N	2025-12-27 12:45:33.059223+08	2025-12-27 15:24:09.135012+08	\N	4
2	CLOSURE	1	COMPLETED	COMPLETED	STUDENT	0	2025-12-27 16:35:25.54402+08	2025-12-27 16:12:16.703329+08	2025-12-27 16:46:57.109184+08	\N	4
\.


--
-- Data for Name: project_progress; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_progress (id, title, content, attachment, created_at, created_by_id, project_id) FROM stdin;
\.


--
-- Data for Name: project_push_records; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_push_records (id, target, payload, response_message, status, created_at, updated_at, project_id) FROM stdin;
\.


--
-- Data for Name: project_recycle_bin; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.project_recycle_bin (id, resource_type, resource_id, payload, attachments, deleted_at, restored_at, is_restored, deleted_by_id, project_id, restored_by_id) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.projects (id, project_no, title, description, is_key_field, self_funding, category_description, start_date, end_date, budget, research_content, research_plan, expected_results, innovation_points, proposal_file, attachment_file, final_report, achievement_file, status, ranking, created_at, updated_at, submitted_at, closure_applied_at, category_id, leader_id, level_id, source_id, year, key_domain_code, mid_term_report, mid_term_submitted_at, approved_budget, batch_id, contract_file, task_book_file, expected_results_data, achievement_summary, discipline_id) FROM stdin;
4	2025METALLURGY0001	镁电解熔盐中杂质的绿色高效分离	熔盐电解法是工业上生产金属镁的常用方法。在电解法生产金属镁的过程中，氯化镁原料和电解槽损耗会引入有害的金属杂质，对镁电解过程产生不利影响。本项目通过控电位电解的方法对熔盐中的Fe(III)、Mn(II)和Al(III)等典型杂质进行分离，为熔盐电解制备高纯度金属镁提供理论依据。采用控电位电解法对NaCl-KCl-MgCl2熔盐中的金属杂质进行分离并计算镁电解质体系中杂质的去除率。	t	0.00		\N	\N	10000.00			调研报告		proposals/WeTab_新标签页.pdf		final_reports/WeTab_新标签页.pdf	achievements/89d5bca79a244f12aade8b3642a3fa01.pdf	CLOSED	\N	2025-12-26 22:21:32.535193+08	2025-12-27 16:46:57.102708+08	2025-12-26 23:21:05.894839+08	2025-12-27 16:42:47.48456+08	8	16	55	1	2025	202406		2025-12-27 12:45:33.039172+08	\N	3			[{"expected_count": 1, "achievement_type": "论文"}]	123	\N
\.


--
-- Data for Name: review_template_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.review_template_items (id, title, description, weight, max_score, is_required, sort_order, created_at, updated_at, template_id) FROM stdin;
\.


--
-- Data for Name: review_templates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.review_templates (id, name, review_type, review_level, scope, description, notice, is_active, is_locked, created_at, updated_at, batch_id, created_by_id, updated_by_id) FROM stdin;
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reviews (id, review_type, review_level, status, comments, score, closure_rating, created_at, reviewed_at, project_id, reviewer_id, phase_instance_id, score_details, review_template_id) FROM stdin;
5	APPLICATION	TEACHER	REJECTED	请补充经费预算明细	\N	\N	2025-12-26 23:06:44.27701+08	2025-12-26 23:15:04.143807+08	4	20	\N	[]	\N
6	APPLICATION	TEACHER	APPROVED	同意申报	\N	\N	2025-12-26 23:21:05.898005+08	2025-12-26 23:25:54.514517+08	4	20	\N	[]	\N
7	APPLICATION	LEVEL2	PENDING		\N	\N	2025-12-26 23:25:54.516754+08	\N	4	\N	\N	[]	\N
8	APPLICATION	LEVEL2	APPROVED	院级评审通过	98	\N	2025-12-26 23:46:25.078908+08	2025-12-26 23:58:09.082679+08	4	22	\N	[]	\N
9	APPLICATION	LEVEL1	PENDING		\N	\N	2025-12-26 23:58:09.085931+08	\N	4	\N	\N	[]	\N
10	APPLICATION	LEVEL1	APPROVED	校级评审通过	95	\N	2025-12-27 00:03:36.89531+08	2025-12-27 00:05:03.403946+08	4	23	\N	[]	\N
11	MID_TERM	TEACHER	APPROVED	中期导师审核通过	\N	\N	2025-12-27 00:36:40.777808+08	2025-12-27 00:39:21.169242+08	4	20	\N	[]	\N
12	MID_TERM	LEVEL2	REJECTED		\N	\N	2025-12-27 00:39:21.180223+08	2025-12-27 12:45:02.569627+08	4	21	\N	[]	\N
13	MID_TERM	TEACHER	APPROVED	通过	\N	\N	2025-12-27 12:45:33.066425+08	2025-12-27 12:46:05.235597+08	4	20	1	[]	\N
14	MID_TERM	LEVEL2	PENDING		\N	\N	2025-12-27 12:46:05.247814+08	\N	4	\N	1	[]	\N
15	MID_TERM	LEVEL2	APPROVED	院级中期审核通过	\N	\N	2025-12-27 13:10:43.353539+08	2025-12-27 13:12:12.99934+08	4	22	1	[]	\N
16	CLOSURE	TEACHER	APPROVED	结题导师审核通过	\N	\N	2025-12-27 16:12:16.708367+08	2025-12-27 16:13:39.05349+08	4	20	2	[]	\N
17	CLOSURE	LEVEL1	PENDING		\N	\N	2025-12-27 16:13:39.056122+08	\N	4	\N	2	[]	\N
18	CLOSURE	LEVEL1	APPROVED	123	90	\N	2025-12-27 16:34:07.996581+08	2025-12-27 16:34:59.122849+08	4	23	2	[]	\N
19	CLOSURE	TEACHER	APPROVED	90	\N	\N	2025-12-27 16:42:47.492429+08	2025-12-27 16:43:06.461989+08	4	20	2	[]	\N
20	CLOSURE	LEVEL2	APPROVED	0	90	\N	2025-12-27 16:43:37.175243+08	2025-12-27 16:44:08.381694+08	4	22	2	[]	\N
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.system_settings (id, code, name, data, is_locked, is_active, created_at, updated_at, updated_by_id, batch_id) FROM stdin;
1	APPLICATION_WINDOW	项目申报时间设置	{"end": "2025-12-25", "start": "2025-12-23", "enabled": true}	f	t	2025-12-24 14:54:21.527563+08	2025-12-24 14:54:22.627171+08	1	\N
2	MIDTERM_WINDOW	中期提交时间设置	{"end": "2025-12-25", "start": "2025-12-23", "enabled": true}	f	t	2025-12-24 14:54:21.546862+08	2025-12-24 14:54:22.646826+08	1	\N
3	CLOSURE_WINDOW	结题提交时间设置	{"end": "2025-12-25", "start": "2025-12-23", "enabled": true}	f	t	2025-12-24 14:54:21.562951+08	2025-12-24 14:54:22.658746+08	1	\N
4	REVIEW_WINDOW	审核时间设置	{"closure": {"level1": {"end": "2025-12-25", "start": "2025-12-23", "enabled": true}, "level2": {"end": "2025-12-25", "start": "2025-12-23", "enabled": true}, "teacher": {"end": "2025-12-25", "start": "2025-12-23", "enabled": true}}, "midterm": {"level2": {"end": "2025-12-25", "start": "2025-12-23", "enabled": true}, "teacher": {"end": "2025-12-25", "start": "2025-12-23", "enabled": true}}, "application": {"level1": {"end": "2025-12-25", "start": "2025-12-23", "enabled": true}, "level2": {"end": "2025-12-25", "start": "2025-12-23", "enabled": true}, "teacher": {"end": "2025-12-25", "start": "2025-12-23", "enabled": true}}}	f	t	2025-12-24 14:54:21.579286+08	2025-12-24 14:54:22.670333+08	1	\N
5	LIMIT_RULES	限制与校验规则	{"max_members": 5, "dedupe_title": true, "max_advisors": 2, "college_quota": {}, "max_student_active": 1, "max_student_member": 1, "max_teacher_active": 5, "advisor_title_required": false, "teacher_excellent_bonus": 0}	f	t	2025-12-24 14:54:21.595625+08	2025-12-24 14:54:22.685558+08	1	\N
6	PROCESS_RULES	流程规则配置	{"reject_to_previous": false, "allow_active_reapply": false, "show_material_in_closure_review": true}	f	t	2025-12-24 14:54:21.609459+08	2025-12-24 14:54:22.701391+08	1	\N
7	REVIEW_RULES	审核规则配置	{"teacher_application_comment_min": 0}	f	t	2025-12-24 14:54:21.623013+08	2025-12-24 14:54:22.715487+08	1	\N
19	REVIEW_WINDOW	审核时间设置	{"closure": {"level1": {"end": "2026-01-31", "start": "2025-12-01", "enabled": true}, "level2": {"end": "2026-01-31", "start": "2025-12-01", "enabled": true}, "teacher": {"end": "2026-01-31", "start": "2025-12-01", "enabled": true}}, "midterm": {"level2": {"end": "2026-01-31", "start": "2025-12-01", "enabled": true}, "teacher": {"end": "2026-01-31", "start": "2025-12-01", "enabled": true}}, "application": {"level1": {"end": "2026-01-31", "start": "2025-12-01", "enabled": true}, "level2": {"end": "2026-01-31", "start": "2025-12-01", "enabled": true}, "teacher": {"end": "2026-01-31", "start": "2025-12-01", "enabled": true}}}	f	t	2025-12-26 21:56:37.45627+08	2025-12-26 22:07:03.418369+08	1	3
20	LIMIT_RULES	限制与校验规则	{"max_members": 5, "dedupe_title": true, "max_advisors": 2, "college_quota": {}, "max_student_active": 1, "max_student_member": 1, "max_teacher_active": 5, "advisor_title_required": false, "teacher_excellent_bonus": 0}	f	t	2025-12-26 21:56:37.471173+08	2025-12-26 22:07:03.431676+08	1	3
21	PROCESS_RULES	流程规则配置	{"reject_to_previous": false, "allow_active_reapply": false, "show_material_in_closure_review": true}	f	t	2025-12-26 21:56:37.488568+08	2025-12-26 22:07:03.44801+08	1	3
22	REVIEW_RULES	审核规则配置	{"teacher_application_comment_min": 0}	f	t	2025-12-26 21:56:37.506499+08	2025-12-26 22:07:03.464329+08	1	3
15	APPLICATION_WINDOW	项目申报时间设置	{"end": "2026-01-31", "start": "2025-12-01", "enabled": true}	f	t	2025-12-26 21:56:37.384786+08	2025-12-26 22:07:03.344464+08	1	3
16	MIDTERM_WINDOW	中期提交时间设置	{"end": "2026-01-31", "start": "2025-12-01", "enabled": true}	f	t	2025-12-26 21:56:37.407741+08	2025-12-26 22:07:03.367456+08	1	3
17	CLOSURE_WINDOW	结题提交时间设置	{"end": "2026-01-31", "start": "2025-12-01", "enabled": true}	f	t	2025-12-26 21:56:37.422189+08	2025-12-26 22:07:03.380131+08	1	3
18	EXPERT_REVIEW_WINDOW	专家评审时间设置	{"end": "2026-01-31", "start": "2025-12-01", "enabled": true}	f	t	2025-12-26 21:56:37.439704+08	2025-12-26 22:07:03.397758+08	1	3
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, password, last_login, is_superuser, username, first_name, last_name, is_staff, date_joined, role, employee_id, real_name, phone, email, major, grade, class_name, college, department, avatar, is_active, created_at, updated_at, title, expert_scope) FROM stdin;
1	pbkdf2_sha256$1200000$34mk2wHfjYAmQmhNASjcbM$U/iJnXcx+Eo7fWrVTZYBKP6D8tI/CacIvdz+BT/f4dI=	\N	t	admin			t	2025-12-16 17:15:53.245779+08	LEVEL1_ADMIN	admin			admin123@qq.com							t	2025-12-16 17:15:53.495549+08	2025-12-16 17:15:53.495554+08		COLLEGE
19	pbkdf2_sha256$1200000$3pUL6tb9PQszikGMOGhXeB$KV46zBzfNqQXHWI4jrH9m1oHxlCmp8bThTuFSPgBJlY=	\N	f	239014243			f	2025-12-24 14:23:22.133196+08	STUDENT	239014243	耿文涛									t	2025-12-24 14:23:22.133385+08	2025-12-24 14:23:22.357852+08		COLLEGE
21	pbkdf2_sha256$1200000$2p3XOH1jvUzCZkhOq2hoBU$JgWJ/sYgqfTabAmRYuK/L5Uh58gNuVkSf0LbzyBysDc=	\N	f	00000001			f	2025-12-24 14:24:55.392936+08	LEVEL2_ADMIN	00000001	张三						METALLURGY			t	2025-12-24 14:24:55.393101+08	2025-12-24 14:24:55.617266+08		COLLEGE
22	pbkdf2_sha256$1200000$19t0LEedWU4KIPSrs46RXh$XLyAvA2xgYQxW0oD9kWA+WWFUlvgBaHaCmJlfS61obQ=	\N	f	20250002			f	2025-12-24 14:25:36.622831+08	EXPERT	20250002	李四						METALLURGY			t	2025-12-24 14:25:36.622989+08	2025-12-24 14:25:36.851639+08	PROFESSOR	COLLEGE
23	pbkdf2_sha256$1200000$HK2wJYyWKpTr77dMX4jd2w$/E9VK9Snkcp0FtKYjMOzcP0Lu6QYozN9GfdK0H91rWM=	\N	f	00000003			f	2025-12-24 14:50:15.286489+08	EXPERT	00000003	王五									t	2025-12-24 14:50:15.286925+08	2025-12-24 14:50:15.540203+08	PROFESSOR	SCHOOL
20	pbkdf2_sha256$1200000$9ATy5kSvdrFWWMnNdaMEpM$d2V+yKb3NyDnu1MUmIolFYgTeqJ9Clj5f2YLM/+0zFI=	\N	f	20250001			f	2025-12-24 14:24:22.87073+08	TEACHER	20250001	华中胜	18225551375	huazs83@163.com				METALLURGY	PROFESSOR		t	2025-12-24 14:24:22.870938+08	2025-12-24 14:24:23.099378+08	PROFESSOR	COLLEGE
17	pbkdf2_sha256$1200000$MPJulnzkB2oIOFany9B7mV$hL46wcYE+tIuWkUFaNsnTpdsLadxfLMhLB9RVzQWiok=	\N	f	229014231			f	2025-12-24 14:22:36.589194+08	STUDENT	229014231	杨竞择									t	2025-12-24 14:22:36.589371+08	2025-12-24 14:22:36.817725+08		COLLEGE
18	pbkdf2_sha256$1200000$cEGGtfI3STTifOZzIqY6EU$LQ+6jg+rFjlMT4Kvot0ZhbkFd+7LyUE42aRLl2logZg=	\N	f	239014352			f	2025-12-24 14:22:58.765389+08	STUDENT	239014352	汤培									t	2025-12-24 14:22:58.765579+08	2025-12-24 14:22:59.009303+08		COLLEGE
16	pbkdf2_sha256$1200000$0CM9UKpWe0Lecv46xAZNEX$hlYfWP4cz7aSbCUSWGTpF25YB3u/Nd+l+kbXZUrVyYQ=	\N	f	229014363			f	2025-12-24 14:22:09.08125+08	STUDENT	229014363	蒋文君	17755531945	2509421760@qq.com	0804			METALLURGY			t	2025-12-24 14:22:09.081497+08	2025-12-24 14:22:09.308072+08		COLLEGE
\.


--
-- Data for Name: users_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: users_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: workflow_configs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.workflow_configs (id, name, phase, version, description, is_active, is_locked, created_at, updated_at, batch_id, created_by_id, updated_by_id) FROM stdin;
\.


--
-- Data for Name: workflow_nodes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.workflow_nodes (id, code, name, node_type, role, review_level, scope, return_policy, notice, sort_order, is_active, created_at, updated_at, review_template_id, workflow_id) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 124, true);


--
-- Name: certificate_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.certificate_settings_id_seq', 1, false);


--
-- Name: dictionary_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dictionary_items_id_seq', 66, true);


--
-- Name: dictionary_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dictionary_types_id_seq', 17, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 31, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 63, true);


--
-- Name: expert_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.expert_groups_id_seq', 2, true);


--
-- Name: expert_groups_members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.expert_groups_members_id_seq', 2, true);


--
-- Name: login_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.login_logs_id_seq', 156, true);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.notifications_id_seq', 12, true);


--
-- Name: project_achievements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_achievements_id_seq', 1, true);


--
-- Name: project_advisors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_advisors_id_seq', 20, true);


--
-- Name: project_archives_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_archives_id_seq', 1, true);


--
-- Name: project_batches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_batches_id_seq', 3, true);


--
-- Name: project_change_requests_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_change_requests_id_seq', 1, false);


--
-- Name: project_change_reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_change_reviews_id_seq', 1, false);


--
-- Name: project_expenditures_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_expenditures_id_seq', 1, false);


--
-- Name: project_members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_members_id_seq', 64, true);


--
-- Name: project_phase_instances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_phase_instances_id_seq', 2, true);


--
-- Name: project_progress_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_progress_id_seq', 1, false);


--
-- Name: project_push_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_push_records_id_seq', 1, false);


--
-- Name: project_recycle_bin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.project_recycle_bin_id_seq', 1, false);


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.projects_id_seq', 4, true);


--
-- Name: review_template_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.review_template_items_id_seq', 1, false);


--
-- Name: review_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.review_templates_id_seq', 1, false);


--
-- Name: reviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reviews_id_seq', 20, true);


--
-- Name: system_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.system_settings_id_seq', 22, true);


--
-- Name: users_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_groups_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 23, true);


--
-- Name: users_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_user_permissions_id_seq', 1, false);


--
-- Name: workflow_configs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.workflow_configs_id_seq', 1, false);


--
-- Name: workflow_nodes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.workflow_nodes_id_seq', 1, false);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: certificate_settings certificate_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.certificate_settings
    ADD CONSTRAINT certificate_settings_pkey PRIMARY KEY (id);


--
-- Name: dictionary_items dictionary_items_dict_type_id_value_d443096c_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dictionary_items
    ADD CONSTRAINT dictionary_items_dict_type_id_value_d443096c_uniq UNIQUE (dict_type_id, value);


--
-- Name: dictionary_items dictionary_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dictionary_items
    ADD CONSTRAINT dictionary_items_pkey PRIMARY KEY (id);


--
-- Name: dictionary_types dictionary_types_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dictionary_types
    ADD CONSTRAINT dictionary_types_code_key UNIQUE (code);


--
-- Name: dictionary_types dictionary_types_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dictionary_types
    ADD CONSTRAINT dictionary_types_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: expert_groups_members expert_groups_members_expertgroup_id_user_id_abc88dfa_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expert_groups_members
    ADD CONSTRAINT expert_groups_members_expertgroup_id_user_id_abc88dfa_uniq UNIQUE (expertgroup_id, user_id);


--
-- Name: expert_groups_members expert_groups_members_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expert_groups_members
    ADD CONSTRAINT expert_groups_members_pkey PRIMARY KEY (id);


--
-- Name: expert_groups expert_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expert_groups
    ADD CONSTRAINT expert_groups_pkey PRIMARY KEY (id);


--
-- Name: login_logs login_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.login_logs
    ADD CONSTRAINT login_logs_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: project_achievements project_achievements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_achievements
    ADD CONSTRAINT project_achievements_pkey PRIMARY KEY (id);


--
-- Name: project_advisors project_advisors_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_advisors
    ADD CONSTRAINT project_advisors_pkey PRIMARY KEY (id);


--
-- Name: project_archives project_archives_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_archives
    ADD CONSTRAINT project_archives_pkey PRIMARY KEY (id);


--
-- Name: project_archives project_archives_project_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_archives
    ADD CONSTRAINT project_archives_project_id_key UNIQUE (project_id);


--
-- Name: project_batches project_batches_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_batches
    ADD CONSTRAINT project_batches_code_key UNIQUE (code);


--
-- Name: project_batches project_batches_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_batches
    ADD CONSTRAINT project_batches_pkey PRIMARY KEY (id);


--
-- Name: project_change_requests project_change_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_change_requests
    ADD CONSTRAINT project_change_requests_pkey PRIMARY KEY (id);


--
-- Name: project_change_reviews project_change_reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_change_reviews
    ADD CONSTRAINT project_change_reviews_pkey PRIMARY KEY (id);


--
-- Name: project_expenditures project_expenditures_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_expenditures
    ADD CONSTRAINT project_expenditures_pkey PRIMARY KEY (id);


--
-- Name: project_members project_members_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_members
    ADD CONSTRAINT project_members_pkey PRIMARY KEY (id);


--
-- Name: project_members project_members_project_id_user_id_ab18bfcc_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_members
    ADD CONSTRAINT project_members_project_id_user_id_ab18bfcc_uniq UNIQUE (project_id, user_id);


--
-- Name: project_phase_instances project_phase_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_phase_instances
    ADD CONSTRAINT project_phase_instances_pkey PRIMARY KEY (id);


--
-- Name: project_progress project_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_progress
    ADD CONSTRAINT project_progress_pkey PRIMARY KEY (id);


--
-- Name: project_push_records project_push_records_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_push_records
    ADD CONSTRAINT project_push_records_pkey PRIMARY KEY (id);


--
-- Name: project_recycle_bin project_recycle_bin_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_recycle_bin
    ADD CONSTRAINT project_recycle_bin_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: projects projects_project_no_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_project_no_key UNIQUE (project_no);


--
-- Name: review_template_items review_template_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_template_items
    ADD CONSTRAINT review_template_items_pkey PRIMARY KEY (id);


--
-- Name: review_templates review_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_templates
    ADD CONSTRAINT review_templates_pkey PRIMARY KEY (id);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_code_batch_id_9901544a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_code_batch_id_9901544a_uniq UNIQUE (code, batch_id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (id);


--
-- Name: project_phase_instances uniq_project_phase_attempt; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_phase_instances
    ADD CONSTRAINT uniq_project_phase_attempt UNIQUE (project_id, phase, attempt_no);


--
-- Name: users users_employee_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_employee_id_key UNIQUE (employee_id);


--
-- Name: users_groups users_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_pkey PRIMARY KEY (id);


--
-- Name: users_groups users_groups_user_id_group_id_fc7788e8_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_user_id_group_id_fc7788e8_uniq UNIQUE (user_id, group_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users_user_permissions users_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: users_user_permissions users_user_permissions_user_id_permission_id_3b86cbdf_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_user_id_permission_id_3b86cbdf_uniq UNIQUE (user_id, permission_id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: workflow_configs workflow_configs_phase_batch_id_version_06d76f32_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_configs
    ADD CONSTRAINT workflow_configs_phase_batch_id_version_06d76f32_uniq UNIQUE (phase, batch_id, version);


--
-- Name: workflow_configs workflow_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_configs
    ADD CONSTRAINT workflow_configs_pkey PRIMARY KEY (id);


--
-- Name: workflow_nodes workflow_nodes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_nodes
    ADD CONSTRAINT workflow_nodes_pkey PRIMARY KEY (id);


--
-- Name: workflow_nodes workflow_nodes_workflow_id_code_63ae61b1_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_nodes
    ADD CONSTRAINT workflow_nodes_workflow_id_code_63ae61b1_uniq UNIQUE (workflow_id, code);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: certificate_settings_project_category_id_eb459b98; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX certificate_settings_project_category_id_eb459b98 ON public.certificate_settings USING btree (project_category_id);


--
-- Name: certificate_settings_project_level_id_0ca1dab1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX certificate_settings_project_level_id_0ca1dab1 ON public.certificate_settings USING btree (project_level_id);


--
-- Name: certificate_settings_updated_by_id_2d83e676; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX certificate_settings_updated_by_id_2d83e676 ON public.certificate_settings USING btree (updated_by_id);


--
-- Name: dictionary__dict_ty_efa91e_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dictionary__dict_ty_efa91e_idx ON public.dictionary_items USING btree (dict_type_id, is_active);


--
-- Name: dictionary_items_dict_type_id_08d3c96f; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dictionary_items_dict_type_id_08d3c96f ON public.dictionary_items USING btree (dict_type_id);


--
-- Name: dictionary_items_value_cc3d1c81; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dictionary_items_value_cc3d1c81 ON public.dictionary_items USING btree (value);


--
-- Name: dictionary_items_value_cc3d1c81_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dictionary_items_value_cc3d1c81_like ON public.dictionary_items USING btree (value varchar_pattern_ops);


--
-- Name: dictionary_types_code_0d0f74a4_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dictionary_types_code_0d0f74a4_like ON public.dictionary_types USING btree (code varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: expert_groups_created_by_id_ea191c03; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX expert_groups_created_by_id_ea191c03 ON public.expert_groups USING btree (created_by_id);


--
-- Name: expert_groups_members_expertgroup_id_c0b06855; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX expert_groups_members_expertgroup_id_c0b06855 ON public.expert_groups_members USING btree (expertgroup_id);


--
-- Name: expert_groups_members_user_id_94d717a7; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX expert_groups_members_user_id_94d717a7 ON public.expert_groups_members USING btree (user_id);


--
-- Name: login_logs_user_id_d31d00a1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX login_logs_user_id_d31d00a1 ON public.login_logs USING btree (user_id);


--
-- Name: notificatio_recipie_583549_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notificatio_recipie_583549_idx ON public.notifications USING btree (recipient_id, is_read);


--
-- Name: notifications_recipient_id_e1133bac; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifications_recipient_id_e1133bac ON public.notifications USING btree (recipient_id);


--
-- Name: notifications_related_project_id_937ebb75; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX notifications_related_project_id_937ebb75 ON public.notifications USING btree (related_project_id);


--
-- Name: project_ach_project_5cdff8_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_ach_project_5cdff8_idx ON public.project_achievements USING btree (project_id, achievement_type_id);


--
-- Name: project_achievements_achievement_type_id_1d76d968; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_achievements_achievement_type_id_1d76d968 ON public.project_achievements USING btree (achievement_type_id);


--
-- Name: project_achievements_project_id_99c3182e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_achievements_project_id_99c3182e ON public.project_achievements USING btree (project_id);


--
-- Name: project_advisors_project_id_d2ef5924; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_advisors_project_id_d2ef5924 ON public.project_advisors USING btree (project_id);


--
-- Name: project_advisors_user_id_e397bc74; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_advisors_user_id_e397bc74 ON public.project_advisors USING btree (user_id);


--
-- Name: project_batches_code_560841e3_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_batches_code_560841e3_like ON public.project_batches USING btree (code varchar_pattern_ops);


--
-- Name: project_change_requests_created_by_id_58f7c62d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_change_requests_created_by_id_58f7c62d ON public.project_change_requests USING btree (created_by_id);


--
-- Name: project_change_requests_project_id_3231f0af; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_change_requests_project_id_3231f0af ON public.project_change_requests USING btree (project_id);


--
-- Name: project_change_reviews_change_request_id_7de00e2e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_change_reviews_change_request_id_7de00e2e ON public.project_change_reviews USING btree (change_request_id);


--
-- Name: project_change_reviews_reviewer_id_3abd4640; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_change_reviews_reviewer_id_3abd4640 ON public.project_change_reviews USING btree (reviewer_id);


--
-- Name: project_exp_project_fcb7bd_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_exp_project_fcb7bd_idx ON public.project_expenditures USING btree (project_id, expenditure_date);


--
-- Name: project_expenditures_category_id_b5d751a0; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_expenditures_category_id_b5d751a0 ON public.project_expenditures USING btree (category_id);


--
-- Name: project_expenditures_created_by_id_283ff779; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_expenditures_created_by_id_283ff779 ON public.project_expenditures USING btree (created_by_id);


--
-- Name: project_expenditures_project_id_6c79dd16; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_expenditures_project_id_6c79dd16 ON public.project_expenditures USING btree (project_id);


--
-- Name: project_members_project_id_bf2e42ec; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_members_project_id_bf2e42ec ON public.project_members USING btree (project_id);


--
-- Name: project_members_user_id_2e9d44b1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_members_user_id_2e9d44b1 ON public.project_members USING btree (user_id);


--
-- Name: project_phase_instances_created_by_id_7783b14c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_phase_instances_created_by_id_7783b14c ON public.project_phase_instances USING btree (created_by_id);


--
-- Name: project_phase_instances_project_id_9f3b1467; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_phase_instances_project_id_9f3b1467 ON public.project_phase_instances USING btree (project_id);


--
-- Name: project_progress_created_by_id_bfa96ce7; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_progress_created_by_id_bfa96ce7 ON public.project_progress USING btree (created_by_id);


--
-- Name: project_progress_project_id_c9b0d403; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_progress_project_id_c9b0d403 ON public.project_progress USING btree (project_id);


--
-- Name: project_push_records_project_id_9dd8de15; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_push_records_project_id_9dd8de15 ON public.project_push_records USING btree (project_id);


--
-- Name: project_recycle_bin_deleted_by_id_5d1409f9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_recycle_bin_deleted_by_id_5d1409f9 ON public.project_recycle_bin USING btree (deleted_by_id);


--
-- Name: project_recycle_bin_project_id_b9c359f1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_recycle_bin_project_id_b9c359f1 ON public.project_recycle_bin USING btree (project_id);


--
-- Name: project_recycle_bin_restored_by_id_2665a121; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX project_recycle_bin_restored_by_id_2665a121 ON public.project_recycle_bin USING btree (restored_by_id);


--
-- Name: projects_batch_id_67b3e4b1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_batch_id_67b3e4b1 ON public.projects USING btree (batch_id);


--
-- Name: projects_category_id_2110ba9e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_category_id_2110ba9e ON public.projects USING btree (category_id);


--
-- Name: projects_discipline_id_a86933e6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_discipline_id_a86933e6 ON public.projects USING btree (discipline_id);


--
-- Name: projects_leader_id_aabb0912; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_leader_id_aabb0912 ON public.projects USING btree (leader_id);


--
-- Name: projects_level_id_8a6f1c0b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_level_id_8a6f1c0b ON public.projects USING btree (level_id);


--
-- Name: projects_project_b2c64d_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_project_b2c64d_idx ON public.projects USING btree (project_no);


--
-- Name: projects_project_no_b1aacc70_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_project_no_b1aacc70_like ON public.projects USING btree (project_no varchar_pattern_ops);


--
-- Name: projects_source_id_4682911e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_source_id_4682911e ON public.projects USING btree (source_id);


--
-- Name: projects_status_6303d7_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX projects_status_6303d7_idx ON public.projects USING btree (status);


--
-- Name: review_template_items_template_id_835bbf34; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX review_template_items_template_id_835bbf34 ON public.review_template_items USING btree (template_id);


--
-- Name: review_templates_batch_id_4ca9aed4; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX review_templates_batch_id_4ca9aed4 ON public.review_templates USING btree (batch_id);


--
-- Name: review_templates_created_by_id_4858a6a0; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX review_templates_created_by_id_4858a6a0 ON public.review_templates USING btree (created_by_id);


--
-- Name: review_templates_updated_by_id_758db1b0; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX review_templates_updated_by_id_758db1b0 ON public.review_templates USING btree (updated_by_id);


--
-- Name: reviews_phase_instance_id_76b853a5; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_phase_instance_id_76b853a5 ON public.reviews USING btree (phase_instance_id);


--
-- Name: reviews_project_1fd85d_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_project_1fd85d_idx ON public.reviews USING btree (project_id, review_level);


--
-- Name: reviews_project_id_1ffdb6d1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_project_id_1ffdb6d1 ON public.reviews USING btree (project_id);


--
-- Name: reviews_review_template_id_2422673c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_review_template_id_2422673c ON public.reviews USING btree (review_template_id);


--
-- Name: reviews_reviewer_id_dbb954a8; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_reviewer_id_dbb954a8 ON public.reviews USING btree (reviewer_id);


--
-- Name: reviews_status_12ddaa_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX reviews_status_12ddaa_idx ON public.reviews USING btree (status);


--
-- Name: system_settings_batch_id_09927f7b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX system_settings_batch_id_09927f7b ON public.system_settings USING btree (batch_id);


--
-- Name: system_settings_updated_by_id_cf1dfbba; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX system_settings_updated_by_id_cf1dfbba ON public.system_settings USING btree (updated_by_id);


--
-- Name: users_employee_id_7c8e0276_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_employee_id_7c8e0276_like ON public.users USING btree (employee_id varchar_pattern_ops);


--
-- Name: users_groups_group_id_2f3517aa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_groups_group_id_2f3517aa ON public.users_groups USING btree (group_id);


--
-- Name: users_groups_user_id_f500bee5; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_groups_user_id_f500bee5 ON public.users_groups USING btree (user_id);


--
-- Name: users_user_permissions_permission_id_6d08dcd2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_user_permissions_permission_id_6d08dcd2 ON public.users_user_permissions USING btree (permission_id);


--
-- Name: users_user_permissions_user_id_92473840; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_user_permissions_user_id_92473840 ON public.users_user_permissions USING btree (user_id);


--
-- Name: users_username_e8658fc8_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX users_username_e8658fc8_like ON public.users USING btree (username varchar_pattern_ops);


--
-- Name: workflow_configs_batch_id_537df69a; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX workflow_configs_batch_id_537df69a ON public.workflow_configs USING btree (batch_id);


--
-- Name: workflow_configs_created_by_id_9ce1a151; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX workflow_configs_created_by_id_9ce1a151 ON public.workflow_configs USING btree (created_by_id);


--
-- Name: workflow_configs_updated_by_id_92af6584; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX workflow_configs_updated_by_id_92af6584 ON public.workflow_configs USING btree (updated_by_id);


--
-- Name: workflow_nodes_review_template_id_bf4b0c22; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX workflow_nodes_review_template_id_bf4b0c22 ON public.workflow_nodes USING btree (review_template_id);


--
-- Name: workflow_nodes_workflow_id_411643ef; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX workflow_nodes_workflow_id_411643ef ON public.workflow_nodes USING btree (workflow_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: certificate_settings certificate_settings_project_category_id_eb459b98_fk_dictionar; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.certificate_settings
    ADD CONSTRAINT certificate_settings_project_category_id_eb459b98_fk_dictionar FOREIGN KEY (project_category_id) REFERENCES public.dictionary_items(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: certificate_settings certificate_settings_project_level_id_0ca1dab1_fk_dictionar; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.certificate_settings
    ADD CONSTRAINT certificate_settings_project_level_id_0ca1dab1_fk_dictionar FOREIGN KEY (project_level_id) REFERENCES public.dictionary_items(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: certificate_settings certificate_settings_updated_by_id_2d83e676_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.certificate_settings
    ADD CONSTRAINT certificate_settings_updated_by_id_2d83e676_fk_users_id FOREIGN KEY (updated_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dictionary_items dictionary_items_dict_type_id_08d3c96f_fk_dictionary_types_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dictionary_items
    ADD CONSTRAINT dictionary_items_dict_type_id_08d3c96f_fk_dictionary_types_id FOREIGN KEY (dict_type_id) REFERENCES public.dictionary_types(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expert_groups expert_groups_created_by_id_ea191c03_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expert_groups
    ADD CONSTRAINT expert_groups_created_by_id_ea191c03_fk_users_id FOREIGN KEY (created_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expert_groups_members expert_groups_member_expertgroup_id_c0b06855_fk_expert_gr; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expert_groups_members
    ADD CONSTRAINT expert_groups_member_expertgroup_id_c0b06855_fk_expert_gr FOREIGN KEY (expertgroup_id) REFERENCES public.expert_groups(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: expert_groups_members expert_groups_members_user_id_94d717a7_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.expert_groups_members
    ADD CONSTRAINT expert_groups_members_user_id_94d717a7_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: login_logs login_logs_user_id_d31d00a1_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.login_logs
    ADD CONSTRAINT login_logs_user_id_d31d00a1_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: notifications notifications_recipient_id_e1133bac_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_recipient_id_e1133bac_fk_users_id FOREIGN KEY (recipient_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: notifications notifications_related_project_id_937ebb75_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_related_project_id_937ebb75_fk_projects_id FOREIGN KEY (related_project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_achievements project_achievements_achievement_type_id_1d76d968_fk_dictionar; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_achievements
    ADD CONSTRAINT project_achievements_achievement_type_id_1d76d968_fk_dictionar FOREIGN KEY (achievement_type_id) REFERENCES public.dictionary_items(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_achievements project_achievements_project_id_99c3182e_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_achievements
    ADD CONSTRAINT project_achievements_project_id_99c3182e_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_advisors project_advisors_project_id_d2ef5924_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_advisors
    ADD CONSTRAINT project_advisors_project_id_d2ef5924_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_advisors project_advisors_user_id_e397bc74_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_advisors
    ADD CONSTRAINT project_advisors_user_id_e397bc74_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_archives project_archives_project_id_9f133d5b_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_archives
    ADD CONSTRAINT project_archives_project_id_9f133d5b_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_change_requests project_change_requests_created_by_id_58f7c62d_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_change_requests
    ADD CONSTRAINT project_change_requests_created_by_id_58f7c62d_fk_users_id FOREIGN KEY (created_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_change_requests project_change_requests_project_id_3231f0af_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_change_requests
    ADD CONSTRAINT project_change_requests_project_id_3231f0af_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_change_reviews project_change_revie_change_request_id_7de00e2e_fk_project_c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_change_reviews
    ADD CONSTRAINT project_change_revie_change_request_id_7de00e2e_fk_project_c FOREIGN KEY (change_request_id) REFERENCES public.project_change_requests(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_change_reviews project_change_reviews_reviewer_id_3abd4640_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_change_reviews
    ADD CONSTRAINT project_change_reviews_reviewer_id_3abd4640_fk_users_id FOREIGN KEY (reviewer_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_expenditures project_expenditures_category_id_b5d751a0_fk_dictionar; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_expenditures
    ADD CONSTRAINT project_expenditures_category_id_b5d751a0_fk_dictionar FOREIGN KEY (category_id) REFERENCES public.dictionary_items(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_expenditures project_expenditures_created_by_id_283ff779_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_expenditures
    ADD CONSTRAINT project_expenditures_created_by_id_283ff779_fk_users_id FOREIGN KEY (created_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_expenditures project_expenditures_project_id_6c79dd16_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_expenditures
    ADD CONSTRAINT project_expenditures_project_id_6c79dd16_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_members project_members_project_id_bf2e42ec_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_members
    ADD CONSTRAINT project_members_project_id_bf2e42ec_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_members project_members_user_id_2e9d44b1_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_members
    ADD CONSTRAINT project_members_user_id_2e9d44b1_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_phase_instances project_phase_instances_created_by_id_7783b14c_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_phase_instances
    ADD CONSTRAINT project_phase_instances_created_by_id_7783b14c_fk_users_id FOREIGN KEY (created_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_phase_instances project_phase_instances_project_id_9f3b1467_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_phase_instances
    ADD CONSTRAINT project_phase_instances_project_id_9f3b1467_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_progress project_progress_created_by_id_bfa96ce7_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_progress
    ADD CONSTRAINT project_progress_created_by_id_bfa96ce7_fk_users_id FOREIGN KEY (created_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_progress project_progress_project_id_c9b0d403_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_progress
    ADD CONSTRAINT project_progress_project_id_c9b0d403_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_push_records project_push_records_project_id_9dd8de15_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_push_records
    ADD CONSTRAINT project_push_records_project_id_9dd8de15_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_recycle_bin project_recycle_bin_deleted_by_id_5d1409f9_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_recycle_bin
    ADD CONSTRAINT project_recycle_bin_deleted_by_id_5d1409f9_fk_users_id FOREIGN KEY (deleted_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_recycle_bin project_recycle_bin_project_id_b9c359f1_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_recycle_bin
    ADD CONSTRAINT project_recycle_bin_project_id_b9c359f1_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: project_recycle_bin project_recycle_bin_restored_by_id_2665a121_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.project_recycle_bin
    ADD CONSTRAINT project_recycle_bin_restored_by_id_2665a121_fk_users_id FOREIGN KEY (restored_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects projects_batch_id_67b3e4b1_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_batch_id_67b3e4b1_fk FOREIGN KEY (batch_id) REFERENCES public.project_batches(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects projects_category_id_2110ba9e_fk_dictionary_items_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_category_id_2110ba9e_fk_dictionary_items_id FOREIGN KEY (category_id) REFERENCES public.dictionary_items(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects projects_discipline_id_a86933e6_fk_dictionary_items_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_discipline_id_a86933e6_fk_dictionary_items_id FOREIGN KEY (discipline_id) REFERENCES public.dictionary_items(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects projects_leader_id_aabb0912_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_leader_id_aabb0912_fk_users_id FOREIGN KEY (leader_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects projects_level_id_8a6f1c0b_fk_dictionary_items_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_level_id_8a6f1c0b_fk_dictionary_items_id FOREIGN KEY (level_id) REFERENCES public.dictionary_items(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: projects projects_source_id_4682911e_fk_dictionary_items_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_source_id_4682911e_fk_dictionary_items_id FOREIGN KEY (source_id) REFERENCES public.dictionary_items(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: review_template_items review_template_item_template_id_835bbf34_fk_review_te; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_template_items
    ADD CONSTRAINT review_template_item_template_id_835bbf34_fk_review_te FOREIGN KEY (template_id) REFERENCES public.review_templates(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: review_templates review_templates_batch_id_4ca9aed4_fk_project_batches_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_templates
    ADD CONSTRAINT review_templates_batch_id_4ca9aed4_fk_project_batches_id FOREIGN KEY (batch_id) REFERENCES public.project_batches(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: review_templates review_templates_created_by_id_4858a6a0_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_templates
    ADD CONSTRAINT review_templates_created_by_id_4858a6a0_fk_users_id FOREIGN KEY (created_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: review_templates review_templates_updated_by_id_758db1b0_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.review_templates
    ADD CONSTRAINT review_templates_updated_by_id_758db1b0_fk_users_id FOREIGN KEY (updated_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews reviews_phase_instance_id_76b853a5_fk_project_p; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_phase_instance_id_76b853a5_fk_project_p FOREIGN KEY (phase_instance_id) REFERENCES public.project_phase_instances(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews reviews_project_id_1ffdb6d1_fk_projects_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_project_id_1ffdb6d1_fk_projects_id FOREIGN KEY (project_id) REFERENCES public.projects(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews reviews_review_template_id_2422673c_fk_review_templates_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_review_template_id_2422673c_fk_review_templates_id FOREIGN KEY (review_template_id) REFERENCES public.review_templates(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: reviews reviews_reviewer_id_dbb954a8_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_reviewer_id_dbb954a8_fk_users_id FOREIGN KEY (reviewer_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: system_settings system_settings_batch_id_09927f7b_fk; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_batch_id_09927f7b_fk FOREIGN KEY (batch_id) REFERENCES public.project_batches(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: system_settings system_settings_updated_by_id_cf1dfbba_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_updated_by_id_cf1dfbba_fk_users_id FOREIGN KEY (updated_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_groups users_groups_group_id_2f3517aa_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_group_id_2f3517aa_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_groups users_groups_user_id_f500bee5_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_groups
    ADD CONSTRAINT users_groups_user_id_f500bee5_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_permissions users_user_permissio_permission_id_6d08dcd2_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissio_permission_id_6d08dcd2_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: users_user_permissions users_user_permissions_user_id_92473840_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users_user_permissions
    ADD CONSTRAINT users_user_permissions_user_id_92473840_fk_users_id FOREIGN KEY (user_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workflow_configs workflow_configs_batch_id_537df69a_fk_project_batches_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_configs
    ADD CONSTRAINT workflow_configs_batch_id_537df69a_fk_project_batches_id FOREIGN KEY (batch_id) REFERENCES public.project_batches(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workflow_configs workflow_configs_created_by_id_9ce1a151_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_configs
    ADD CONSTRAINT workflow_configs_created_by_id_9ce1a151_fk_users_id FOREIGN KEY (created_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workflow_configs workflow_configs_updated_by_id_92af6584_fk_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_configs
    ADD CONSTRAINT workflow_configs_updated_by_id_92af6584_fk_users_id FOREIGN KEY (updated_by_id) REFERENCES public.users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workflow_nodes workflow_nodes_review_template_id_bf4b0c22_fk_review_te; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_nodes
    ADD CONSTRAINT workflow_nodes_review_template_id_bf4b0c22_fk_review_te FOREIGN KEY (review_template_id) REFERENCES public.review_templates(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: workflow_nodes workflow_nodes_workflow_id_411643ef_fk_workflow_configs_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workflow_nodes
    ADD CONSTRAINT workflow_nodes_workflow_id_411643ef_fk_workflow_configs_id FOREIGN KEY (workflow_id) REFERENCES public.workflow_configs(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

\unrestrict vp9ptfVMwPFzmfZErZvFRD0BpUOIEpyh0Z3sa7BtvCrRfIifkRpKfMo8cybCSxS

