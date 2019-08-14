/*
 Navicat MySQL Data Transfer

 Source Server         : Tencent
 Source Server Type    : MySQL
 Source Server Version : 50628
 Source Host           : 5780e03864e11.sh.cdb.myqcloud.com:4201
 Source Schema         : multimedia

 Target Server Type    : MySQL
 Target Server Version : 50628
 File Encoding         : 65001

 Date: 28/07/2019 19:55:42
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for tokens
-- ----------------------------
DROP TABLE IF EXISTS `tokens`;
CREATE TABLE `tokens`  (
  `token` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'token值',
  `phone` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '对应用户',
  `createdtime` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `expiration` bigint(20) NULL DEFAULT NULL COMMENT '过期时间',
  `counting` int(11) NULL DEFAULT NULL COMMENT 'token计数',
  `enduring` tinyint(4) NULL DEFAULT NULL COMMENT '是否长效',
  PRIMARY KEY (`token`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

SET FOREIGN_KEY_CHECKS = 1;
