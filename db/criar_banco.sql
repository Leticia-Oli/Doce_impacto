CREATE DATABASE IF NOT EXISTS DOCE_IMPACTO;

USE DOCE_IMPACTO;

CREATE TABLE IF NOT EXISTS USUARIOS(
    ID INTEGER NOT NULL AUTO_INCREMENT,
    NOME VARCHAR(100) NOT NULL,
    EMAIL VARCHAR(100) NOT NULL UNIQUE,
    SENHA VARCHAR(100) NOT NULL,
    TELEFONE BIGINT NOT NULL,
    SEXO VARCHAR(1),
    DATA_NASC DATE,
    CURSO_CARGO VARCHAR(100),
    TURNO VARCHAR(100),
    TIPO TINYINT NOT NULL,

    PRIMARY KEY(ID)
);

CREATE TABLE IF NOT EXISTS CAD_PRODUTO(
    ID INTEGER NOT NULL AUTO_INCREMENT,
    PRODUTO VARCHAR(100) NOT NULL,
    PRECO VARCHAR(100) NOT NULL,
    DESCRICAO VARCHAR(100),
    CATEGORIA VARCHAR(100),
    IMAGEM LONGBLOB,
    PRIMARY KEY(ID)
);

SET character_set_client = utf8;
SET character_set_connection = utf8;
SET character_set_results = utf8;
SET collation_connection = utf8;

INSERT INTO USUARIOS(NOME, EMAIL, SENHA, TELEFONE, TIPO)
VALUES('ADM', 'ADM@EMAIL', 'SENHA123##', 99999, 0);
