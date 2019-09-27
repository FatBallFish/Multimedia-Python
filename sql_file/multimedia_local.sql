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

 Date: 27/09/2019 14:05:32
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for active_users
-- ----------------------------
DROP TABLE IF EXISTS `active_users`;
CREATE TABLE `active_users`  (
  `active_id` int(8) NOT NULL COMMENT '8位活动id',
  `user_id` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '32位用户id',
  `join_time` datetime(0) NOT NULL COMMENT '加入时间'
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Records of active_users
-- ----------------------------
INSERT INTO `active_users` VALUES (78554587, '13750687010', '2019-08-25 12:06:38');
INSERT INTO `active_users` VALUES (59795779, '13566284913', '2019-09-21 19:33:45');
INSERT INTO `active_users` VALUES (78251505, '13750687010', '2019-09-22 02:25:38');
INSERT INTO `active_users` VALUES (59795779, '13750687010', '2019-09-22 02:45:10');
INSERT INTO `active_users` VALUES (59795779, '17816064319', '2019-09-23 15:07:55');
INSERT INTO `active_users` VALUES (78554587, '17816064319', '2019-09-23 15:08:09');
INSERT INTO `active_users` VALUES (59795779, '15925868186', '2019-09-25 16:34:53');
INSERT INTO `active_users` VALUES (78554587, '15925868186', '2019-09-25 16:35:00');

-- ----------------------------
-- Table structure for bbs_active
-- ----------------------------
DROP TABLE IF EXISTS `bbs_active`;
CREATE TABLE `bbs_active`  (
  `active_id` int(11) NOT NULL COMMENT '7位id',
  `user_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `content` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `start_time` datetime(0) NULL DEFAULT NULL,
  `end_time` datetime(0) NULL DEFAULT NULL,
  `create_time` datetime(0) NOT NULL,
  `update_time` datetime(0) NOT NULL,
  PRIMARY KEY (`active_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Records of bbs_active
-- ----------------------------
INSERT INTO `bbs_active` VALUES (59795779, '13566284913', '阿斯达', '<p>阿斯达</p>', '2019-09-04 12:00:00', '2019-09-25 12:00:00', '2019-09-21 14:04:49', '2019-09-21 14:04:49');
INSERT INTO `bbs_active` VALUES (78554587, '13750687010', '校友召集令2', '恰逢更名时机，召集校友来此一聚，更新活动内容', '2019-08-25 00:00:00', '2019-08-26 00:00:00', '2019-08-24 15:29:57', '2019-08-24 16:13:14');

-- ----------------------------
-- Table structure for bbs_article
-- ----------------------------
DROP TABLE IF EXISTS `bbs_article`;
CREATE TABLE `bbs_article`  (
  `article_id` bigint(10) NOT NULL COMMENT '10位时间戳',
  `user_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户id',
  `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '文章标题',
  `content` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '文章内容',
  `create_time` datetime(0) NOT NULL COMMENT '创建时间',
  `update_time` datetime(0) NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`article_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Records of bbs_article
-- ----------------------------
INSERT INTO `bbs_article` VALUES (1565926081, '13750687010', '紫阳街游记', '<!doctype html>\n<html>\n<head>\n<meta charset=\'UTF-8\'><meta name=\'viewport\' content=\'width=device-width initial-scale=1\'>\n<title></title></head>\n<body><p>这次暑假是个十分有意义的暑假，我们一行四人相约临海——这座千年古城，共同探索枧桥鼓的路迹。</p>\n<p>我们来到了紫阳古街，这里真不愧是历史古城。</p>\n<p>&nbsp;</p>\n<p>这里有一面大鼓立于古街的十字路口，仿佛镇门兽般守护着这条千年古街，这座千年古城。</p>\n</body>\n</html>', '2019-08-16 11:28:01', '2019-08-16 11:28:01');
INSERT INTO `bbs_article` VALUES (1568546112, '15925868186', '枧桥董村游记', '<!doctype html>\n<html>\n<head>\n<meta charset=\'UTF-8\'><meta name=\'viewport\' content=\'width=device-width initial-scale=1\'>\n<title></title></head>\n<body><p>择一事终一生...</p>\n<p>守心一处止于此间</p>\n<p>匠人...匠心...</p>\n<p>守护岁月记忆</p>\n<p>传承千年故事...</p>\n<p>#董村枧桥鼓之行#  </p>\n</body>\n</html>', '2019-09-15 19:15:12', '2019-09-15 19:15:12');
INSERT INTO `bbs_article` VALUES (1568613052, '13750687010', '五小灵童', '<p><img src=\"https://multimedia-1251848017.cos.ap-shanghai.myqcloud.com/article/13705687010-20190316001.JPG\" style=\"max-width:100%;\"><br></p>', '2019-09-16 13:50:52', '2019-09-16 13:50:52');
INSERT INTO `bbs_article` VALUES (1569516693, '17816064319', '遇见·枧桥鼓', '<p>那日骄阳似火，忽而狂风大作，暴雨袭来。白墙黑瓦之下，唯有一抹亮红映在记忆里，挥之不去。<br><br>大大小小的鼓，清一色圆墩墩的模样，憨态可掬。乍一看，似乎都是一样的红色，一样的鼓圈，一样的鼓槌……可当我细细看去，用手轻轻拂过每一个鼓，它们却又是全然不同的。红色的漆料涂抹于鼓身，每一笔，每一划，都留下了细微但不同的纹路；鼓身上的鼓圈不同大小，不同形状，也有不同的颜色；紧绷的鼓皮摸上去也有着不同的质感；甚至于鼓槌，也绝不是一个模子里刻出来的。<br><br>这大概是手工制作的独特魅力。<br><br>跟随谢哲长师傅来到他制鼓的地方：红色的漆，金色的铆钉，黑色的布鞋……在轰隆作响的机器轰鸣中，在漫天飞舞的木屑灰尘中，一滴滴凝聚着匠人心血的汗珠落在了木材上，溶进了还未制成的鼓身上。<br><br>你听那鼓声铮铮，声声敲进匠人的一生；你看那泱泱华夏，处处印在国人的心田。<br></p>', '2019-09-27 00:51:33', '2019-09-27 00:51:33');

-- ----------------------------
-- Table structure for bbs_comment
-- ----------------------------
DROP TABLE IF EXISTS `bbs_comment`;
CREATE TABLE `bbs_comment`  (
  `article_id` bigint(20) NOT NULL COMMENT '文章id',
  `comment_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '评论id，使用MD5，32位',
  `father_id` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '评论父id，用于楼中楼回复',
  `user_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户id',
  `content` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '评论内容',
  `create_time` datetime(0) NOT NULL COMMENT '创建时间',
  `update_time` datetime(0) NOT NULL COMMENT '更新时间',
  PRIMARY KEY (`comment_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Records of bbs_comment
-- ----------------------------
INSERT INTO `bbs_comment` VALUES (1568601876, '1544a4f7aeca682b2a1d1e10c870a913', '', '13566284913', '<p>啦啦啦</p>', '2019-09-16 11:46:26', '2019-09-16 11:46:26');
INSERT INTO `bbs_comment` VALUES (1565926081, '1aa6ddf68bea87f2305dd9fd5d3bb2c8', '', '13750687010', '这是一条测试评论', '2019-08-18 09:32:16', '2019-08-18 09:32:16');
INSERT INTO `bbs_comment` VALUES (1568546112, '26ca95fa49dbbc2320d16deb8543e1f6', '', '13566284913', '<p>阿斯达</p>', '2019-09-16 01:55:00', '2019-09-16 01:55:00');
INSERT INTO `bbs_comment` VALUES (1565926081, '354b6ded0748cd837d0ebf06230b9770', '76bd7b76fcd0b23f3d171f39b416d936', '13750687010', '这是一条用API请求的子级评论', '2019-08-18 11:27:59', '2019-08-18 11:27:59');
INSERT INTO `bbs_comment` VALUES (1568546112, '581d293ac9c9829b39a3ee7f7b74a03a', '', '13750687010', '<p>喜欢枧桥鼓</p>', '2019-09-16 03:51:38', '2019-09-16 03:51:38');
INSERT INTO `bbs_comment` VALUES (1568613052, '5886fc9ef8663f7a02e2b4ba592eb855', '', '13566284913', '<p>lllll</p>', '2019-09-16 13:59:51', '2019-09-16 13:59:51');
INSERT INTO `bbs_comment` VALUES (1568599386, '614ce26e73d03b2f303e48e5522a41e9', '', '13566284913', '<p>说得对说得对</p>', '2019-09-16 10:27:12', '2019-09-16 10:27:12');
INSERT INTO `bbs_comment` VALUES (1565926081, '76bd7b76fcd0b23f3d171f39b416d936', '', '13750687010', '这是一条更新过的评论', '2019-08-18 09:41:41', '2019-08-18 11:08:43');
INSERT INTO `bbs_comment` VALUES (1565926081, '96cfda55b759fa94f55268a8047d6845', '76bd7b76fcd0b23f3d171f39b416d936', '13750687010', '这是一条用API请求的子级评论', '2019-08-18 09:42:21', '2019-08-18 09:42:21');
INSERT INTO `bbs_comment` VALUES (1565926081, 'd757d9ea4c9c1860299a0341524a6a7d', 'a301c03e1248eabf83785b5548d603ec', '13750687010', '这是一条用API更新的子级评论2', '2019-08-18 09:38:09', '2019-08-18 11:49:05');
INSERT INTO `bbs_comment` VALUES (1568605615, 'e987d5b2b53cb70853a6a320ab5d91ed', '', '13566284913', '<p>啦啦啦</p>', '2019-09-16 12:04:08', '2019-09-16 12:04:08');
INSERT INTO `bbs_comment` VALUES (1568599386, 'f4ed5c6403fb6361037510a4f7c5f80b', '', '13750687010', '<p>这是一条测试评论</p>', '2019-09-16 10:05:01', '2019-09-16 10:05:01');

-- ----------------------------
-- Table structure for tokens
-- ----------------------------
DROP TABLE IF EXISTS `tokens`;
CREATE TABLE `tokens`  (
  `token` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'token值，32位',
  `phone` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '对应用户',
  `createdtime` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `expiration` bigint(20) NULL DEFAULT NULL COMMENT '过期时间',
  `counting` int(11) NULL DEFAULT NULL COMMENT 'token计数',
  `enduring` tinyint(4) NULL DEFAULT NULL COMMENT '是否长效',
  PRIMARY KEY (`token`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Records of tokens
-- ----------------------------
INSERT INTO `tokens` VALUES ('99c9150238fa21051f558ceccad55b8a', '13750687010', '2019-08-15 10:39:07', 1569091813, 1, 1);
INSERT INTO `tokens` VALUES ('e5ca02d9605e80c2edb5dc99cc8e798d', '13750687010', '2019-09-27 13:04:21', 1569561262, 1, 0);

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `phone` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '11位手机号',
  `password` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'MD5加密',
  `createdtime` datetime(0) NOT NULL COMMENT '创建时间',
  `group` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户组',
  `salt` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '盐',
  PRIMARY KEY (`phone`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '用户账号信息' ROW_FORMAT = Compact;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES ('13566284913', '2af23c78f579eadcf7c1a8fcf323ab07', '2019-08-20 23:50:37', '__NORMAL__', 'I97irn4v68');
INSERT INTO `users` VALUES ('13750687010', '323f1c556bb3338b0881fc39b01b8664', '2019-07-26 22:23:06', '__ADMIN__', 'eu0SUawvZ3');
INSERT INTO `users` VALUES ('15857174214', '273b6eced4679b0b045bc941f06ccb43', '2019-09-12 17:27:03', '__NORMAL__', 'VINaIqk426');
INSERT INTO `users` VALUES ('15925868186', '5c375e57fc5afc5091b8a9dc482f7140', '2019-09-16 00:17:50', '__ADMIN__', 'hRx12Rl82q');
INSERT INTO `users` VALUES ('17767174231', '26a3d090d484a3d030c2db16ccac777e', '2019-08-25 17:56:34', '__NORMAL__', '8NS1dJWim1');
INSERT INTO `users` VALUES ('17816064319', '8e6e9e75ef64d0f7bc9a4c8570ed1ff7', '2019-09-13 12:27:23', '__NORMAL__', 'Kf2l85rnwD');

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

-- ----------------------------
-- Records of usersinfo
-- ----------------------------
INSERT INTO `usersinfo` VALUES ('13566284913', '许淳皓', '许大帅哥', '1010549831@qq.com', 1);
INSERT INTO `usersinfo` VALUES ('13750687010', '王凌超', 'FatBallFish', '893721708@qq.com', 1);
INSERT INTO `usersinfo` VALUES ('15857174214', NULL, NULL, NULL, 1);
INSERT INTO `usersinfo` VALUES ('15925868186', '徐罗燕', 'chungmu road', NULL, 1);
INSERT INTO `usersinfo` VALUES ('17767174231', NULL, NULL, NULL, 1);
INSERT INTO `usersinfo` VALUES ('17816064319', '钱丹', '蛋蛋', '3391791582@qq.com', 1);

SET FOREIGN_KEY_CHECKS = 1;
