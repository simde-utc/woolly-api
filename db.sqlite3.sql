
USE woolly;
CREATE TABLE IF NOT EXISTS `sales_sale` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`name`	varchar (200) NOT NULL,
	`description`	varchar ( 1000 ) NOT NULL,
	`creation_date`	date NOT NULL,
	`begin_date`	date NOT NULL,
	`end_date`	date NOT NULL,
	`max_payment_date`	date NOT NULL,
	`max_item_quantity`	integer NOT NULL,
	`association_id`	integer NOT NULL,
	`paymentmethods_id`	integer NOT NULL,
	FOREIGN KEY(`paymentmethods_id`) REFERENCES `sales_paymentmethod`(`id`),
	FOREIGN KEY(`association_id`) REFERENCES `sales_association`(`id`)
);
INSERT INTO `sales_sale` VALUES (1,'SDF','Une description','2017-06-05','2017-06-05','2017-06-30','2017-06-30',4000,1,1);
INSERT INTO `sales_sale` VALUES (2,'Futuroscope','Sale permission test','2017-06-10','2017-06-10','2017-06-30','2017-06-30',89,1,1);
CREATE TABLE IF NOT EXISTS `sales_paymentmethod` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`name`	varchar ( 200 ) NOT NULL,
	`api_url`	varchar ( 500 ) NOT NULL
);
INSERT INTO `sales_paymentmethod` VALUES (1,'PayUT','mettreuneurlici');
INSERT INTO `sales_paymentmethod` VALUES (2,'Cash','');
CREATE TABLE IF NOT EXISTS `sales_orderline` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`quantity`	integer NOT NULL,
	`item_id`	integer NOT NULL,
	`order_id`	integer NOT NULL,
	FOREIGN KEY(`item_id`) REFERENCES `sales_item`(`id`),
	FOREIGN KEY(`order_id`) REFERENCES `sales_order`(`id`)
);
INSERT INTO `sales_orderline` VALUES (1,1,1,1);
INSERT INTO `sales_orderline` VALUES (2,23,1,2);
INSERT INTO `sales_orderline` VALUES (3,10,1,12);
INSERT INTO `sales_orderline` VALUES (4,20,2,11);
INSERT INTO `sales_orderline` VALUES (5,12,1,13);
INSERT INTO `sales_orderline` VALUES (6,24,2,13);
CREATE TABLE IF NOT EXISTS `sales_order` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`status`	varchar ( 50 ) NOT NULL,
	`date`	date NOT NULL,
	`owner_id`	integer NOT NULL,
	FOREIGN KEY(`owner_id`) REFERENCES `authentication_woollyuser`(`id`)
);
INSERT INTO `sales_order` VALUES (1,'awaiting_validation','2017-06-09',1);
INSERT INTO `sales_order` VALUES (2,'not_payed','2017-06-09',3);
INSERT INTO `sales_order` VALUES (3,'TestLines2','2017-06-15',1);
INSERT INTO `sales_order` VALUES (4,'TestLines5','2017-06-15',1);
INSERT INTO `sales_order` VALUES (5,'TestLines6','2017-06-15',1);
INSERT INTO `sales_order` VALUES (6,'TestLines6','2017-06-15',1);
INSERT INTO `sales_order` VALUES (7,'TestLines7','2017-06-15',1);
INSERT INTO `sales_order` VALUES (8,'TestLines8','2017-06-15',1);
INSERT INTO `sales_order` VALUES (9,'TestLines9','2017-06-15',1);
INSERT INTO `sales_order` VALUES (10,'TestLines10','2017-06-15',1);
INSERT INTO `sales_order` VALUES (11,'TestLines11','2017-06-15',1);
INSERT INTO `sales_order` VALUES (12,'Awaiting_validation','2017-06-17',1);
INSERT INTO `sales_order` VALUES (13,'TestLines12','2017-06-15',1);
CREATE TABLE IF NOT EXISTS `sales_itemspecifications` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`quantity`	integer NOT NULL,
	`price`	real NOT NULL,
	`item_id`	integer NOT NULL,
	`nemopay_id`	varchar ( 30 ) NOT NULL,
	`woolly_user_type_id`	integer NOT NULL,
	FOREIGN KEY(`woolly_user_type_id`) REFERENCES `authentication_woollyusertype`(`id`),
	FOREIGN KEY(`item_id`) REFERENCES `sales_item`(`id`)
);
INSERT INTO `sales_itemspecifications` VALUES (1,4000,12.0,1,'0',1);
INSERT INTO `sales_itemspecifications` VALUES (2,89,15.0,2,'0',3);
INSERT INTO `sales_itemspecifications` VALUES (3,28,18.0,1,'0',2);
CREATE TABLE IF NOT EXISTS `sales_item` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`name`	varchar ( 200 ) NOT NULL,
	`description`	varchar ( 1000 ) NOT NULL,
	`remaining_quantity`	integer NOT NULL,
	`initial_quantity`	integer NOT NULL,
	`sale_id`	integer NOT NULL,
	FOREIGN KEY(`sale_id`) REFERENCES `sales_sale`(`id`)
);
INSERT INTO `sales_item` VALUES (1,'Billet Cotisant','Une description cotisant',4000,4000,1);
INSERT INTO `sales_item` VALUES (2,'Billet Tremplin','un billet pour les cotisants tremplin',89,89,2);
INSERT INTO `sales_item` VALUES (3,'Billet Non Cotisant SDF','azdaz,dazlkd',28,39,1);
CREATE TABLE IF NOT EXISTS `sales_associationmember` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`role`	varchar ( 50 ) NOT NULL,
	`rights`	varchar ( 50 ) NOT NULL,
	`association_id`	integer NOT NULL,
	`woollyUser_id`	integer NOT NULL,
	FOREIGN KEY(`association_id`) REFERENCES `sales_association`(`id`),
	FOREIGN KEY(`woollyUser_id`) REFERENCES `authentication_woollyuser`(`id`)
);
INSERT INTO `sales_associationmember` VALUES (1,'Member','All',1,1);
CREATE TABLE IF NOT EXISTS `sales_association` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`name`	varchar ( 200 ) NOT NULL,
	`bank_account`	varchar ( 30 ) NOT NULL,
	`foundation_id`	varchar ( 30 ) NOT NULL
);
INSERT INTO `sales_association` VALUES (1,'SDF','1231414','0');
CREATE TABLE IF NOT EXISTS `django_session` (
	`session_key`	varchar ( 40 ) NOT NULL,
	`session_data`	text NOT NULL,
	`expire_date`	datetime NOT NULL,
	PRIMARY KEY(`session_key`)
);
INSERT INTO `django_session` VALUES ('lkir3eoirmqvw0apvxs2hr4qh8s76mq5','YjBiZmUzMWRkZDc0MTAyZWI3Y2U0YWYwNDYwMDFhMTExYjBlNzg5Yzp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYmFja2VuZHMuR2luZ2VyQ0FTQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6IjA4YmY4ZTZlZjg5ZDlhZjIxZTExNmVkMmRkN2FkZTViODEyYWNjNmMifQ==','2017-06-19 12:59:53.427355');
INSERT INTO `django_session` VALUES ('2nfeprclzcqcpd7axf94fbeado8ccsm4','ZTdiZGM1ZGJlODMwOGYyMjVlNDY3YWYwOTI3OTNjYjZjMTc1NzJmMzp7Il9hdXRoX3VzZXJfaWQiOiIyIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYmFja2VuZHMuR2luZ2VyQ0FTQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImExNTZkMDgyYWRiODFlODM1N2M2NWY5YmJiOTM4ZTNmOTQ1OWYyZjYifQ==','2017-06-20 09:30:45.701531');
INSERT INTO `django_session` VALUES ('wll3x9rf60543sudokoi0a64dtfpbwae','NDRjZWYzMWVkMDdjYWRkNWFhNzMzYmFjM2FjZWVkMmZjODNmMTZjZjp7Il9hdXRoX3VzZXJfaGFzaCI6ImExNTZkMDgyYWRiODFlODM1N2M2NWY5YmJiOTM4ZTNmOTQ1OWYyZjYiLCJfYXV0aF91c2VyX2lkIjoiMiIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImF1dGhlbnRpY2F0aW9uLmJhY2tlbmRzLkdpbmdlckNBU0JhY2tlbmQifQ==','2017-06-21 08:02:38.985676');
INSERT INTO `django_session` VALUES ('oxho8b2v6slqwih41sxe07nkj7bb66jp','YjBiZmUzMWRkZDc0MTAyZWI3Y2U0YWYwNDYwMDFhMTExYjBlNzg5Yzp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYmFja2VuZHMuR2luZ2VyQ0FTQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6IjA4YmY4ZTZlZjg5ZDlhZjIxZTExNmVkMmRkN2FkZTViODEyYWNjNmMifQ==','2017-06-26 07:18:24.402048');
INSERT INTO `django_session` VALUES ('oq6jp8nbw626twxkacq45pa6g0vfcnsu','OThmZGMxMTBiYTNlNDc0OTVmYmZmOGIyYTIwNGI2MDFmZGNiZTUwZDp7Il9hdXRoX3VzZXJfYmFja2VuZCI6ImF1dGhlbnRpY2F0aW9uLmJhY2tlbmRzLkdpbmdlckNBU0JhY2tlbmQiLCJfYXV0aF91c2VyX2lkIjoiMyIsIl9hdXRoX3VzZXJfaGFzaCI6ImVhZDRkNzk0YzI3N2M1ZGRiN2YwYzE4MTdlZTZmYWNjOTY3NzViNzEifQ==','2017-06-29 17:01:58.441193');
INSERT INTO `django_session` VALUES ('st75ad9g0dkiokqksefyyw7azkcxs88v','NDRjZWYzMWVkMDdjYWRkNWFhNzMzYmFjM2FjZWVkMmZjODNmMTZjZjp7Il9hdXRoX3VzZXJfaGFzaCI6ImExNTZkMDgyYWRiODFlODM1N2M2NWY5YmJiOTM4ZTNmOTQ1OWYyZjYiLCJfYXV0aF91c2VyX2lkIjoiMiIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImF1dGhlbnRpY2F0aW9uLmJhY2tlbmRzLkdpbmdlckNBU0JhY2tlbmQifQ==','2017-06-29 17:20:51.560251');
INSERT INTO `django_session` VALUES ('6224qq5b41bi0zw4c4k8up7eu2maqm18','YjBiZmUzMWRkZDc0MTAyZWI3Y2U0YWYwNDYwMDFhMTExYjBlNzg5Yzp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYmFja2VuZHMuR2luZ2VyQ0FTQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6IjA4YmY4ZTZlZjg5ZDlhZjIxZTExNmVkMmRkN2FkZTViODEyYWNjNmMifQ==','2017-06-30 21:35:19.319022');
INSERT INTO `django_session` VALUES ('82akwqci15q7z5qxczbqy49mkl2xnplt','ZTdiZGM1ZGJlODMwOGYyMjVlNDY3YWYwOTI3OTNjYjZjMTc1NzJmMzp7Il9hdXRoX3VzZXJfaWQiOiIyIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiYXV0aGVudGljYXRpb24uYmFja2VuZHMuR2luZ2VyQ0FTQmFja2VuZCIsIl9hdXRoX3VzZXJfaGFzaCI6ImExNTZkMDgyYWRiODFlODM1N2M2NWY5YmJiOTM4ZTNmOTQ1OWYyZjYifQ==','2017-10-13 08:32:59.168746');
INSERT INTO `django_session` VALUES ('fvy9vjv4u17xvvxnhcxtiex7rejuxkdp','MzRmOTVlMzE2ODE2YTk5YzE1NGMwZThmMDNhZWRlNGFkMjQ2NDNjYTp7Il9hdXRoX3VzZXJfaWQiOiI0IiwiX2F1dGhfdXNlcl9oYXNoIjoiZTg3ZjYwZDdlNTIyYzRmY2I1ZDQ1ZDgzNjk3YjUyNmIzMDE3OTMyMCIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImF1dGhlbnRpY2F0aW9uLmJhY2tlbmRzLkdpbmdlckNBU0JhY2tlbmQifQ==','2017-11-18 15:13:47.901661');
INSERT INTO `django_session` VALUES ('ec7xu3d6okutc53t0tzg8lw8yolwr6mo','ZjQyNThmZjVmNTUwOWM0YzY3OTgyMjlkNzc1ZmVkYzc0ZmYxZDhhNzp7Il9hdXRoX3VzZXJfYmFja2VuZCI6ImF1dGhlbnRpY2F0aW9uLmJhY2tlbmRzLkdpbmdlckNBU0JhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJlODdmNjBkN2U1MjJjNGZjYjVkNDVkODM2OTdiNTI2YjMwMTc5MzIwIiwiX2F1dGhfdXNlcl9pZCI6IjQifQ==','2017-12-06 08:32:46.900192');
CREATE TABLE IF NOT EXISTS `django_migrations` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`app`	varchar ( 255 ) NOT NULL,
	`name`	varchar ( 255 ) NOT NULL,
	`applied`	datetime NOT NULL
);
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2017-06-05 12:40:39.447404');
INSERT INTO `django_migrations` VALUES (2,'authentication','0001_initial','2017-06-05 12:40:39.461386');
INSERT INTO `django_migrations` VALUES (3,'admin','0001_initial','2017-06-05 12:40:39.488681');
INSERT INTO `django_migrations` VALUES (4,'admin','0002_logentry_remove_auto_add','2017-06-05 12:40:39.505434');
INSERT INTO `django_migrations` VALUES (5,'contenttypes','0002_remove_content_type_name','2017-06-05 12:40:39.528670');
INSERT INTO `django_migrations` VALUES (6,'auth','0001_initial','2017-06-05 12:40:39.573145');
INSERT INTO `django_migrations` VALUES (7,'auth','0002_alter_permission_name_max_length','2017-06-05 12:40:39.598174');
INSERT INTO `django_migrations` VALUES (8,'auth','0003_alter_user_email_max_length','2017-06-05 12:40:39.607084');
INSERT INTO `django_migrations` VALUES (9,'auth','0004_alter_user_username_opts','2017-06-05 12:40:39.615758');
INSERT INTO `django_migrations` VALUES (10,'auth','0005_alter_user_last_login_null','2017-06-05 12:40:39.624374');
INSERT INTO `django_migrations` VALUES (11,'auth','0006_require_contenttypes_0002','2017-06-05 12:40:39.627531');
INSERT INTO `django_migrations` VALUES (12,'auth','0007_alter_validators_add_error_messages','2017-06-05 12:40:39.641143');
INSERT INTO `django_migrations` VALUES (13,'auth','0008_alter_user_username_max_length','2017-06-05 12:40:39.655566');
INSERT INTO `django_migrations` VALUES (14,'core','0001_initial','2017-06-05 12:40:39.821724');
INSERT INTO `django_migrations` VALUES (15,'core','0002_remove_woollyuser_type','2017-06-05 12:40:39.854753');
INSERT INTO `django_migrations` VALUES (16,'core','0003_woollyuser_type','2017-06-05 12:40:39.889910');
INSERT INTO `django_migrations` VALUES (17,'core','0004_order_items','2017-06-05 12:40:39.936622');
INSERT INTO `django_migrations` VALUES (18,'core','0005_auto_20170514_2140','2017-06-05 12:40:39.988749');
INSERT INTO `django_migrations` VALUES (19,'core','0006_auto_20170518_1430','2017-06-05 12:40:40.005341');
INSERT INTO `django_migrations` VALUES (20,'core','0007_auto_20170518_1441','2017-06-05 12:40:40.054091');
INSERT INTO `django_migrations` VALUES (21,'core','0008_auto_20170518_1444','2017-06-05 12:40:40.067815');
INSERT INTO `django_migrations` VALUES (22,'core','0009_auto_20170519_1140','2017-06-05 12:40:40.141371');
INSERT INTO `django_migrations` VALUES (23,'core','0010_remove_associationmember_association','2017-06-05 12:40:40.175089');
INSERT INTO `django_migrations` VALUES (24,'core','0011_auto_20170521_1039','2017-06-05 12:40:40.207839');
INSERT INTO `django_migrations` VALUES (25,'core','0012_associationmember','2017-06-05 12:40:40.248001');
INSERT INTO `django_migrations` VALUES (26,'core','0009_auto_20170526_0706','2017-06-05 12:40:40.310510');
INSERT INTO `django_migrations` VALUES (27,'core','0010_woollyuser_birthdate','2017-06-05 12:40:40.329561');
INSERT INTO `django_migrations` VALUES (28,'core','0011_auto_20170526_0948','2017-06-05 12:40:40.377285');
INSERT INTO `django_migrations` VALUES (29,'core','0013_merge_20170530_1423','2017-06-05 12:40:40.381111');
INSERT INTO `django_migrations` VALUES (30,'core','0013_merge_20170529_1114','2017-06-05 12:40:40.385152');
INSERT INTO `django_migrations` VALUES (31,'core','0014_merge_20170601_1220','2017-06-05 12:40:40.388349');
INSERT INTO `django_migrations` VALUES (32,'core','0015_auto_20170601_1220','2017-06-05 12:40:40.417787');
INSERT INTO `django_migrations` VALUES (33,'core','0016_auto_20170605_1240','2017-06-05 12:40:40.607346');
INSERT INTO `django_migrations` VALUES (34,'sales','0001_initial','2017-06-05 12:40:40.661862');
INSERT INTO `django_migrations` VALUES (35,'sales','0002_auto_20170522_1014','2017-06-05 12:40:40.677319');
INSERT INTO `django_migrations` VALUES (36,'sales','0003_item_sale','2017-06-05 12:40:40.701715');
INSERT INTO `django_migrations` VALUES (37,'sales','0004_auto_20170522_1142','2017-06-05 12:40:40.723112');
INSERT INTO `django_migrations` VALUES (38,'sales','0005_auto_20170522_1351','2017-06-05 12:40:40.739928');
INSERT INTO `django_migrations` VALUES (39,'sales','0006_auto_20170522_1352','2017-06-05 12:40:40.759498');
INSERT INTO `django_migrations` VALUES (40,'sales','0007_auto_20170522_1434','2017-06-05 12:40:40.822639');
INSERT INTO `django_migrations` VALUES (41,'sales','0008_auto_20170522_1443','2017-06-05 12:40:40.843673');
INSERT INTO `django_migrations` VALUES (42,'sales','0009_auto_20170522_2133','2017-06-05 12:40:40.858743');
INSERT INTO `django_migrations` VALUES (43,'sales','0010_auto_20170522_2149','2017-06-05 12:40:40.876573');
INSERT INTO `django_migrations` VALUES (44,'sales','0011_me','2017-06-05 12:40:40.886313');
INSERT INTO `django_migrations` VALUES (45,'sales','0012_delete_me','2017-06-05 12:40:40.897997');
INSERT INTO `django_migrations` VALUES (46,'sales','0013_auto_20170524_0527','2017-06-05 12:40:40.921271');
INSERT INTO `django_migrations` VALUES (47,'sales','0014_auto_20170524_0529','2017-06-05 12:40:40.945780');
INSERT INTO `django_migrations` VALUES (48,'sales','0015_auto_20170526_1507','2017-06-05 12:40:40.970187');
INSERT INTO `django_migrations` VALUES (49,'sales','0016_auto_20170529_0737','2017-06-05 12:40:40.983453');
INSERT INTO `django_migrations` VALUES (50,'sales','0017_order_orderline_paymentmethod','2017-06-05 12:40:41.020598');
INSERT INTO `django_migrations` VALUES (51,'sales','0018_auto_20170605_1240','2017-06-05 12:40:41.086689');
INSERT INTO `django_migrations` VALUES (52,'sessions','0001_initial','2017-06-05 12:40:41.097908');
INSERT INTO `django_migrations` VALUES (53,'sales','0002_remove_orderline_item','2017-06-09 06:05:26.831737');
INSERT INTO `django_migrations` VALUES (54,'sales','0003_orderline_item','2017-06-09 06:05:26.866312');
INSERT INTO `django_migrations` VALUES (55,'sales','0004_order_members','2017-06-09 06:05:26.901210');
INSERT INTO `django_migrations` VALUES (56,'sales','0005_remove_order_members','2017-06-09 06:05:26.930106');
INSERT INTO `django_migrations` VALUES (57,'sales','0006_order_owner','2017-06-09 06:05:26.961751');
INSERT INTO `django_migrations` VALUES (58,'sales','0007_remove_order_quantity','2017-06-09 06:05:26.986781');
INSERT INTO `django_migrations` VALUES (59,'authentication','0002_auto_20170609_0715','2017-06-09 07:15:30.275809');
INSERT INTO `django_migrations` VALUES (60,'sales','0008_auto_20170609_0715','2017-06-09 07:15:30.320668');
INSERT INTO `django_migrations` VALUES (61,'sales','0009_sale_payment_methods','2017-06-09 07:53:05.766398');
INSERT INTO `django_migrations` VALUES (62,'sales','0010_auto_20170609_0814','2017-06-09 08:14:53.002778');
INSERT INTO `django_migrations` VALUES (63,'sales','0011_auto_20170609_0836','2017-06-09 08:36:11.746115');
INSERT INTO `django_migrations` VALUES (64,'sales','0012_auto_20170609_0900','2017-06-09 09:00:37.391326');
INSERT INTO `django_migrations` VALUES (65,'sales','0013_associationmember','2017-06-10 19:05:51.965418');
INSERT INTO `django_migrations` VALUES (66,'sales','0014_auto_20170615_1954','2017-06-15 22:24:47.164031');
INSERT INTO `django_migrations` VALUES (67,'sales','0015_auto_20170615_2001','2017-06-15 22:24:47.221054');
INSERT INTO `django_migrations` VALUES (68,'sales','0016_auto_20170615_2005','2017-06-15 22:24:47.259858');
INSERT INTO `django_migrations` VALUES (69,'authentication','0003_auto_20170616_1432','2017-06-16 14:33:02.485303');
INSERT INTO `django_migrations` VALUES (70,'sales','0017_auto_20170616_1443','2017-06-16 14:43:18.497557');
INSERT INTO `django_migrations` VALUES (71,'sales','0018_auto_20170616_1450','2017-06-16 14:50:21.000105');
INSERT INTO `django_migrations` VALUES (72,'authentication','0004_woollyuser_associations','2017-06-17 10:18:59.274092');
CREATE TABLE IF NOT EXISTS `django_content_type` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`app_label`	varchar ( 100 ) NOT NULL,
	`model`	varchar ( 100 ) NOT NULL
);
INSERT INTO `django_content_type` VALUES (1,'admin','logentry');
INSERT INTO `django_content_type` VALUES (2,'auth','permission');
INSERT INTO `django_content_type` VALUES (3,'auth','group');
INSERT INTO `django_content_type` VALUES (4,'contenttypes','contenttype');
INSERT INTO `django_content_type` VALUES (5,'sessions','session');
INSERT INTO `django_content_type` VALUES (6,'cas','tgt');
INSERT INTO `django_content_type` VALUES (7,'cas','pgtiou');
INSERT INTO `django_content_type` VALUES (8,'authentication','woollyuser');
INSERT INTO `django_content_type` VALUES (9,'authentication','woollyusertype');
INSERT INTO `django_content_type` VALUES (10,'sales','association');
INSERT INTO `django_content_type` VALUES (11,'sales','item');
INSERT INTO `django_content_type` VALUES (12,'sales','itemspecifications');
INSERT INTO `django_content_type` VALUES (13,'sales','sale');
INSERT INTO `django_content_type` VALUES (14,'sales','order');
INSERT INTO `django_content_type` VALUES (15,'sales','orderline');
INSERT INTO `django_content_type` VALUES (16,'sales','paymentmethod');
INSERT INTO `django_content_type` VALUES (17,'sales','associationmember');
CREATE TABLE IF NOT EXISTS `django_admin_log` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`object_id`	text,
	`object_repr`	varchar ( 200 ) NOT NULL,
	`action_flag`	smallint unsigned NOT NULL,
	`change_message`	text NOT NULL,
	`content_type_id`	integer,
	`user_id`	integer NOT NULL,
	`action_time`	datetime NOT NULL,
	FOREIGN KEY(`user_id`) REFERENCES `authentication_woollyuser`(`id`),
	FOREIGN KEY(`content_type_id`) REFERENCES `django_content_type`(`id`)
);
INSERT INTO `django_admin_log` VALUES (1,'1','Association object',1,'[{"added": {}}]',10,1,'2017-06-05 13:26:55.868351');
INSERT INTO `django_admin_log` VALUES (2,'1','Sale object',1,'[{"added": {}}]',13,1,'2017-06-05 13:27:34.241910');
INSERT INTO `django_admin_log` VALUES (3,'1','Item object',1,'[{"added": {}}]',11,1,'2017-06-05 13:28:43.400078');
INSERT INTO `django_admin_log` VALUES (4,'1','ItemSpecifications object',1,'[{"added": {}}]',12,1,'2017-06-05 13:29:09.092282');
INSERT INTO `django_admin_log` VALUES (5,'1','ItemSpecifications object',2,'[{"changed": {"fields": ["woolly_user_type"]}}]',12,1,'2017-06-05 13:30:04.358208');
INSERT INTO `django_admin_log` VALUES (6,'1','Order object',1,'[{"added": {}}]',14,1,'2017-06-09 07:18:48.714135');
INSERT INTO `django_admin_log` VALUES (7,'1','OrderLine object',1,'[{"added": {}}]',15,1,'2017-06-09 07:19:21.399584');
INSERT INTO `django_admin_log` VALUES (8,'2','Order object',1,'[{"added": {}}]',14,1,'2017-06-09 07:20:02.486572');
INSERT INTO `django_admin_log` VALUES (9,'2','OrderLine object',1,'[{"added": {}}]',15,1,'2017-06-09 07:20:21.819984');
INSERT INTO `django_admin_log` VALUES (10,'2','OrderLine object',2,'[{"changed": {"fields": ["order"]}}]',15,1,'2017-06-09 07:21:10.432067');
INSERT INTO `django_admin_log` VALUES (11,'2','OrderLine object',2,'[{"changed": {"fields": ["order"]}}]',15,1,'2017-06-09 07:29:22.314829');
INSERT INTO `django_admin_log` VALUES (12,'1','PaymentMethod object',1,'[{"added": {}}]',16,1,'2017-06-09 07:54:17.316628');
INSERT INTO `django_admin_log` VALUES (13,'2','PaymentMethod object',1,'[{"added": {}}]',16,1,'2017-06-09 08:15:03.994263');
INSERT INTO `django_admin_log` VALUES (14,'2','Sale object',1,'[{"added": {}}]',13,1,'2017-06-10 07:38:46.081993');
INSERT INTO `django_admin_log` VALUES (15,'2','Item object',1,'[{"added": {}}]',11,1,'2017-06-10 07:39:47.898144');
INSERT INTO `django_admin_log` VALUES (16,'2','Item object',2,'[{"changed": {"fields": ["sale"]}}]',11,1,'2017-06-10 07:40:33.244478');
INSERT INTO `django_admin_log` VALUES (17,'2','ItemSpecifications object',1,'[{"added": {}}]',12,1,'2017-06-10 07:41:56.567911');
INSERT INTO `django_admin_log` VALUES (18,'2','ItemSpecifications object',2,'[{"changed": {"fields": ["item"]}}]',12,1,'2017-06-10 07:42:17.953946');
INSERT INTO `django_admin_log` VALUES (19,'1','ItemSpecifications object',2,'[{"changed": {"fields": ["woolly_user_type"]}}]',12,1,'2017-06-10 07:47:14.889462');
INSERT INTO `django_admin_log` VALUES (20,'2','ItemSpecifications object',2,'[{"changed": {"fields": ["woolly_user_type"]}}]',12,1,'2017-06-10 07:47:26.558005');
INSERT INTO `django_admin_log` VALUES (21,'3','Item object',1,'[{"added": {}}]',11,1,'2017-06-10 08:34:56.292950');
INSERT INTO `django_admin_log` VALUES (22,'2','ItemSpecifications object',2,'[{"changed": {"fields": ["woolly_user_type"]}}]',12,1,'2017-06-10 08:36:07.122962');
INSERT INTO `django_admin_log` VALUES (23,'3','ItemSpecifications object',1,'[{"added": {}}]',12,1,'2017-06-10 08:36:41.652374');
INSERT INTO `django_admin_log` VALUES (24,'2','ItemSpecifications object',2,'[{"changed": {"fields": ["woolly_user_type"]}}]',12,1,'2017-06-10 08:36:59.869009');
INSERT INTO `django_admin_log` VALUES (25,'3','ItemSpecifications object',2,'[{"changed": {"fields": ["woolly_user_type"]}}]',12,1,'2017-06-10 08:39:58.112042');
INSERT INTO `django_admin_log` VALUES (26,'1','ItemSpecifications object',2,'[{"changed": {"fields": ["woolly_user_type"]}}]',12,1,'2017-06-10 08:40:46.148547');
INSERT INTO `django_admin_log` VALUES (27,'1','AssociationMember object',1,'[{"added": {}}]',17,1,'2017-06-12 07:26:44.280935');
INSERT INTO `django_admin_log` VALUES (28,'2','Order object',2,'[{"changed": {"fields": ["status"]}}]',14,1,'2017-06-15 22:27:42.044625');
INSERT INTO `django_admin_log` VALUES (29,'1','Order object',2,'[{"changed": {"fields": ["status"]}}]',14,1,'2017-06-15 22:27:56.793324');
CREATE TABLE IF NOT EXISTS `authentication_woollyusertype` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`name`	varchar ( 50 ) NOT NULL UNIQUE
);
INSERT INTO `authentication_woollyusertype` VALUES (1,'cotisant');
INSERT INTO `authentication_woollyusertype` VALUES (2,'non-cotisant');
INSERT INTO `authentication_woollyusertype` VALUES (3,'tremplin');
INSERT INTO `authentication_woollyusertype` VALUES (4,'exterieur');
CREATE TABLE IF NOT EXISTS `authentication_woollyuser` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`password`	varchar ( 128 ) NOT NULL,
	`last_login`	datetime,
	`login`	varchar ( 253 ) NOT NULL UNIQUE,
	`last_name`	varchar ( 100 ) NOT NULL,
	`first_name`	varchar ( 100 ) NOT NULL,
	`email`	varchar ( 254 ) NOT NULL,
	`birthdate`	date NOT NULL,
	`is_active`	bool NOT NULL,
	`is_admin`	bool NOT NULL,
	`woollyusertype_id`	integer NOT NULL,
	FOREIGN KEY(`woollyusertype_id`) REFERENCES `authentication_woollyusertype`(`id`)
);
INSERT INTO `authentication_woollyuser` VALUES (1,'pbkdf2_sha256$36000$CdO9JA7PSCPm$BSPKRQzUcjDkKzLiCwyVDjbmMOcu3AWs8d88eK7wemM=','2017-06-16 21:35:19.316595','flcartie','Cartier','Florian','florian.cartier@etu.utc.fr','0001-01-01',1,1,1);
INSERT INTO `authentication_woollyuser` VALUES (2,'pbkdf2_sha256$36000$LIEYHEkVgajj$GNnr4tENE2ASt9wDJGs9qVwbg4V/cYfpIZ8O1eGldlo=','2017-09-29 08:32:59.067947','tbarizie','Barizien','Thomas','thomas.barizien@etu.utc.fr','0001-01-01',1,0,1);
INSERT INTO `authentication_woollyuser` VALUES (3,'pbkdf2_sha256$36000$jD2nW4N85IoO$Ijzxd/wmymBmg4JTjnf0o2CX830GJE9lhg9Xgi7qfjc=','2017-06-15 17:11:52.015756','edepuiff','De puiffe de magondeaux','Estelle','estelle.de-puiffe-de-magondeaux@etu.utc.fr','0001-01-01',1,1,1);
INSERT INTO `authentication_woollyuser` VALUES (4,'pbkdf2_sha256$36000$e4l1rWflr03C$2NJ0AxB8eZK5J7heIBRvr5JSPont/yg2GzDn2wuUuxA=','2017-11-22 08:32:46.876773','hadefala','Hadef','Alaric','alaric.hadef@etu.utc.fr','0001-01-01',1,0,1);
CREATE TABLE IF NOT EXISTS `auth_permission` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`content_type_id`	integer NOT NULL,
	`codename`	varchar ( 100 ) NOT NULL,
	`name`	varchar ( 255 ) NOT NULL,
	FOREIGN KEY(`content_type_id`) REFERENCES `django_content_type`(`id`)
);
INSERT INTO `auth_permission` VALUES (1,1,'add_logentry','Can add log entry');
INSERT INTO `auth_permission` VALUES (2,1,'change_logentry','Can change log entry');
INSERT INTO `auth_permission` VALUES (3,1,'delete_logentry','Can delete log entry');
INSERT INTO `auth_permission` VALUES (4,2,'add_permission','Can add permission');
INSERT INTO `auth_permission` VALUES (5,2,'change_permission','Can change permission');
INSERT INTO `auth_permission` VALUES (6,2,'delete_permission','Can delete permission');
INSERT INTO `auth_permission` VALUES (7,3,'add_group','Can add group');
INSERT INTO `auth_permission` VALUES (8,3,'change_group','Can change group');
INSERT INTO `auth_permission` VALUES (9,3,'delete_group','Can delete group');
INSERT INTO `auth_permission` VALUES (10,4,'add_contenttype','Can add content type');
INSERT INTO `auth_permission` VALUES (11,4,'change_contenttype','Can change content type');
INSERT INTO `auth_permission` VALUES (12,4,'delete_contenttype','Can delete content type');
INSERT INTO `auth_permission` VALUES (13,5,'add_session','Can add session');
INSERT INTO `auth_permission` VALUES (14,5,'change_session','Can change session');
INSERT INTO `auth_permission` VALUES (15,5,'delete_session','Can delete session');
INSERT INTO `auth_permission` VALUES (16,6,'add_tgt','Can add tgt');
INSERT INTO `auth_permission` VALUES (17,6,'change_tgt','Can change tgt');
INSERT INTO `auth_permission` VALUES (18,6,'delete_tgt','Can delete tgt');
INSERT INTO `auth_permission` VALUES (19,7,'add_pgtiou','Can add pgt iou');
INSERT INTO `auth_permission` VALUES (20,7,'change_pgtiou','Can change pgt iou');
INSERT INTO `auth_permission` VALUES (21,7,'delete_pgtiou','Can delete pgt iou');
INSERT INTO `auth_permission` VALUES (22,8,'add_woollyuser','Can add woolly user');
INSERT INTO `auth_permission` VALUES (23,8,'change_woollyuser','Can change woolly user');
INSERT INTO `auth_permission` VALUES (24,8,'delete_woollyuser','Can delete woolly user');
INSERT INTO `auth_permission` VALUES (25,9,'add_woollyusertype','Can add woolly user type');
INSERT INTO `auth_permission` VALUES (26,9,'change_woollyusertype','Can change woolly user type');
INSERT INTO `auth_permission` VALUES (27,9,'delete_woollyusertype','Can delete woolly user type');
INSERT INTO `auth_permission` VALUES (28,10,'add_association','Can add association');
INSERT INTO `auth_permission` VALUES (29,10,'change_association','Can change association');
INSERT INTO `auth_permission` VALUES (30,10,'delete_association','Can delete association');
INSERT INTO `auth_permission` VALUES (31,11,'add_item','Can add item');
INSERT INTO `auth_permission` VALUES (32,11,'change_item','Can change item');
INSERT INTO `auth_permission` VALUES (33,11,'delete_item','Can delete item');
INSERT INTO `auth_permission` VALUES (34,12,'add_itemspecifications','Can add item specifications');
INSERT INTO `auth_permission` VALUES (35,12,'change_itemspecifications','Can change item specifications');
INSERT INTO `auth_permission` VALUES (36,12,'delete_itemspecifications','Can delete item specifications');
INSERT INTO `auth_permission` VALUES (37,13,'add_sale','Can add sale');
INSERT INTO `auth_permission` VALUES (38,13,'change_sale','Can change sale');
INSERT INTO `auth_permission` VALUES (39,13,'delete_sale','Can delete sale');
INSERT INTO `auth_permission` VALUES (40,14,'add_order','Can add order');
INSERT INTO `auth_permission` VALUES (41,14,'change_order','Can change order');
INSERT INTO `auth_permission` VALUES (42,14,'delete_order','Can delete order');
INSERT INTO `auth_permission` VALUES (43,15,'add_orderline','Can add order line');
INSERT INTO `auth_permission` VALUES (44,15,'change_orderline','Can change order line');
INSERT INTO `auth_permission` VALUES (45,15,'delete_orderline','Can delete order line');
INSERT INTO `auth_permission` VALUES (46,16,'add_paymentmethod','Can add payment method');
INSERT INTO `auth_permission` VALUES (47,16,'change_paymentmethod','Can change payment method');
INSERT INTO `auth_permission` VALUES (48,16,'delete_paymentmethod','Can delete payment method');
INSERT INTO `auth_permission` VALUES (49,17,'add_associationmember','Can add association member');
INSERT INTO `auth_permission` VALUES (50,17,'change_associationmember','Can change association member');
INSERT INTO `auth_permission` VALUES (51,17,'delete_associationmember','Can delete association member');
CREATE TABLE IF NOT EXISTS `auth_group_permissions` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`group_id`	integer NOT NULL,
	`permission_id`	integer NOT NULL,
	FOREIGN KEY(`permission_id`) REFERENCES `auth_permission`(`id`),
	FOREIGN KEY(`group_id`) REFERENCES `auth_group`(`id`)
);
CREATE TABLE IF NOT EXISTS `auth_group` (
	`id`	integer NOT NULL PRIMARY KEY AUTO_INCREMENT,
	`name`	varchar ( 80 ) NOT NULL UNIQUE
);
