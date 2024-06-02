-- Adminer 4.8.1 PostgreSQL 16.3 (Debian 16.3-1.pgdg120+1) dump

DROP TABLE IF EXISTS "cartas_app_equipo";
DROP SEQUENCE IF EXISTS "cartas_app_equipo_id_seq";
CREATE SEQUENCE "cartas_app_equipo_id_seq" INCREMENT 1 START 4 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
CREATE TABLE "public"."cartas_app_equipo" (
    "id" bigint DEFAULT nextval('cartas_app_equipo_id_seq') NOT NULL,
    "nombre" character varying(250) NOT NULL,
    "liga" character varying(250) NOT NULL,
    "pais" character varying(150) NOT NULL,
    "escudo" character varying(500) NOT NULL,
    "createdAt" timestamptz NOT NULL,
    "updatedAt" timestamptz NOT NULL,
    "isActive" boolean NOT NULL,
    CONSTRAINT "cartas_app_equipo_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

INSERT INTO "cartas_app_equipo" ("id", "nombre", "liga", "pais", "escudo", "createdAt", "updatedAt", "isActive") VALUES
(3,	'FC Barcelona',	'La Liga',	'Spain',	'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRj7kHgyd9GHcPpVcJ8FMmOjOQVk6JyHMq3Rw&s',	'2024-05-31 17:05:34.364245+00',	'2024-06-01 17:02:47.234209+00',	't'),
(2,	'Al Nassar',	'Arabia Pro League',	'Arabia Saudita',	'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRj7kHgyd9GHcPpVcJ8FMmOjOQVk6JyHMq3Rw&s',	'2024-05-31 17:12:03.067433+00',	'2024-06-01 17:02:49.761658+00',	't'),
(1,	'Inter Miami',	'MSL',	'USA',	'https://images.mlssoccer.com/image/private/t_q-best/mls-mia-prd/zvachkwh374kxisjezra.png',	'2024-05-30 16:30:16.292154+00',	'2024-06-01 17:02:51.722618+00',	't');

DROP TABLE IF EXISTS "cartas_app_jugador";
DROP SEQUENCE IF EXISTS "cartas_app_jugador_id_seq";
CREATE SEQUENCE "cartas_app_jugador_id_seq" INCREMENT 1 START 4 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
CREATE TABLE "public"."cartas_app_jugador" (
    "id" bigint DEFAULT nextval('cartas_app_jugador_id_seq') NOT NULL,
    "nombreCompleto" character varying(250) NOT NULL,
    "edad" integer NOT NULL,
    "media" integer NOT NULL,
    "rareza" character varying(250) NOT NULL,
    "imagen" character varying(100),
    "valor" numeric(10,2) NOT NULL,
    "posicion" character varying(3) NOT NULL,
    "createdAt" timestamptz NOT NULL,
    "updatedAt" timestamptz NOT NULL,
    "isActive" boolean NOT NULL,
    "equipo_id" bigint NOT NULL,
    CONSTRAINT "cartas_app_jugador_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

CREATE INDEX "cartas_app_jugador_equipo_id_032515b3" ON "public"."cartas_app_jugador" USING btree ("equipo_id");

INSERT INTO "cartas_app_jugador" ("id", "nombreCompleto", "edad", "media", "rareza", "imagen", "valor", "posicion", "createdAt", "updatedAt", "isActive", "equipo_id") VALUES
(2,	'Dembele',	27,	83,	'Común',	'',	50000.00,	'ED',	'2024-05-31 07:34:03.129274+00',	'2024-06-01 17:02:59.854287+00',	't',	3),
(1,	'Leo Messi',	35,	95,	'Épica',	'',	1000000.00,	'ED',	'2024-05-31 17:02:18.531303+00',	'2024-06-01 17:03:01.828437+00',	't',	1);

DROP TABLE IF EXISTS "user_app_account";
DROP SEQUENCE IF EXISTS "user_app_account_id_seq";
CREATE SEQUENCE "user_app_account_id_seq" INCREMENT 1 START 3 MINVALUE 1 MAXVALUE 9223372036854775807 CACHE 1;
CREATE TABLE "public"."user_app_account" (
    "id" bigint DEFAULT nextval('user_app_account_id_seq') NOT NULL,
    "password" character varying(128) NOT NULL,
    "first_name" character varying(50) NOT NULL,
    "last_name" character varying(50) NOT NULL,
    "username" character varying(50) NOT NULL,
    "email" character varying(50) NOT NULL,
    "phone_number" character varying(50) NOT NULL,
    "date_joined" timestamptz NOT NULL,
    "last_login" timestamptz NOT NULL,
    "is_admin" boolean NOT NULL,
    "is_staff" boolean NOT NULL,
    "is_active" boolean NOT NULL,
    "is_superuser" boolean NOT NULL,
    "futcoins" numeric(10,2) NOT NULL,
    CONSTRAINT "user_app_account_email_key" UNIQUE ("email"),
    CONSTRAINT "user_app_account_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "user_app_account_username_key" UNIQUE ("username")
) WITH (oids = false);

CREATE INDEX "user_app_account_email_2bb28c32_like" ON "public"."user_app_account" USING btree ("email");

CREATE INDEX "user_app_account_username_0546db4a_like" ON "public"."user_app_account" USING btree ("username");

INSERT INTO "user_app_account" ("id", "password", "first_name", "last_name", "username", "email", "phone_number", "date_joined", "last_login", "is_admin", "is_staff", "is_active", "is_superuser", "futcoins") VALUES
(2,	'pbkdf2_sha256$720000$5rejdJAdRF6FztvKAOYoRv$M5g2KBVdZhpAabw0O5cJNTwzCQzEf5pYmqMdWbuyH5o=',	'Leo',	'Messi',	'leomessi10',	'messiantonella@gmail.com',	'100000000',	'2024-05-30 16:34:43.406274+00',	'2024-05-30 16:34:43.421683+00',	'f',	'f',	't',	'f',	0.00),
(1,	'pbkdf2_sha256$720000$CueG6HCibHKvmcz3kO7Q8i$n1HhtD9btZsT5yuT1wbldEQWprefo7ipvV5WuslgndA=',	'Mohamed',	'El Kasmi',	'mohaek10',	'elkasmimoha@gmail.com',	'',	'2024-05-30 16:07:55.157548+00',	'2024-05-30 20:50:58.021764+00',	't',	't',	't',	't',	0.00);

ALTER TABLE ONLY "public"."cartas_app_jugador" ADD CONSTRAINT "cartas_app_jugador_equipo_id_032515b3_fk_cartas_app_equipo_id" FOREIGN KEY (equipo_id) REFERENCES cartas_app_equipo(id) DEFERRABLE INITIALLY DEFERRED DEFERRABLE;

-- 2024-06-02 10:09:03.01718+00