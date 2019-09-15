/*
 Navicat MySQL Data Transfer

 Source Server         : dmt
 Source Server Type    : MySQL
 Source Server Version : 50628
 Source Host           : 5780e03864e11.sh.cdb.myqcloud.com:4201
 Source Schema         : multimedia

 Target Server Type    : MySQL
 Target Server Version : 50628
 File Encoding         : 65001

 Date: 14/09/2019 01:57:23
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for usersinfo
-- ----------------------------
DROP TABLE IF EXISTS `usersinfo`;
CREATE TABLE `usersinfo`  (
  `phone` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '账号',
  `name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '姓名',
  `nickname` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '昵称',
  `email` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '邮箱',
  `level` int(11) NOT NULL COMMENT '用户等级',
  PRIMARY KEY (`phone`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '用户账号' ROW_FORMAT = Compact;

SET FOREIGN_KEY_CHECKS = 1;
