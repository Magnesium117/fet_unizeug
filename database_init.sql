CREATE DATABASE Unizeug;
USE Unizeug;
CREATE TABLE LVAs(id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,lvid VARCHAR(6), lvname VARCHAR(256), lvpath VARCHAR(256),PRIMARY KEY(id));
CREATE TABLE Profs(id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,name VARCHAR(256),PRIMARY KEY(id));
CREATE TABLE LPLink(id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,LId bigint(20),PId bigint(20),PRIMARY KEY(id));
CREATE TABLE SubCats(id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,LId BIGINT(20),PId BIGINT(20),cat TINYINT UNSIGNED,name VARCHAR(256), PRIMARY KEY(id));
CREATE TABLE FIP(id UUID DEFAULT(UUID()), filename VARCHAR(256), filetype VARCHAR(8),initTimeStamp DATETIME, PRIMARY KEY(id));
