SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
USE `menu`;
-- ----------------------------
-- Table structure for menu_items
-- ----------------------------
DROP TABLE IF EXISTS `menu_items`;
CREATE TABLE `menu_items`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '菜品ID，主键自增',
  `dish_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜品名称',
  `price` decimal(8, 2) NOT NULL COMMENT '价格（元）',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '菜品描述',
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '菜品分类',
  `spice_level` tinyint NULL DEFAULT 0 COMMENT '辣度等级：0-不辣，1-微辣，2-中辣，3-重辣',
  `flavor` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '口味特点',
  `main_ingredients` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '主要食材，多个食材用逗号分隔',
  `cooking_method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '烹饪方法',
  `is_vegetarian` tinyint(1) NULL DEFAULT 0 COMMENT '是否素食：0-否，1-是',
  `allergens` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '过敏原信息，多个过敏原用逗号分隔',
  `is_available` tinyint(1) NULL DEFAULT 1 COMMENT '是否可供应：0-不可用，1-可用',
  `is_featured` tinyint(1) NULL DEFAULT 0 COMMENT '是否特色主菜：0-否，1-是',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_category`(`category`) USING BTREE,
  INDEX `idx_is_available`(`is_available`) USING BTREE,
  INDEX `idx_is_vegetarian`(`is_vegetarian`) USING BTREE,
  INDEX `idx_price`(`price`) USING BTREE,
  INDEX `idx_spice_level`(`spice_level`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '菜单表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of menu_items
-- ----------------------------
INSERT INTO `menu_items` VALUES (1, '宫保鸡丁', 28.00, '经典川菜，鸡肉丁配花生米，酸甜微辣，口感丰富', '川菜', 2, '酸甜微辣', '鸡胸肉,花生米,青椒,红椒,葱段', '爆炒', 0, '花生,可能含有麸质', 1,1,now(),now());
INSERT INTO `menu_items` VALUES (2, '麻婆豆腐', 18.00, '四川传统名菜，嫩滑豆腐配麻辣汤汁，下饭神器', '川菜', 3, '麻辣鲜香', '嫩豆腐,牛肉末,豆瓣酱,花椒', '烧炒', 0, '大豆,可能含有麸质', 1, 0,now(),now());
INSERT INTO `menu_items` VALUES (3, '清炒时蔬', 15.00, '新鲜时令蔬菜清炒，营养健康，口感清爽', '素食', 0, '清淡爽口', '时令蔬菜,蒜蓉', '清炒', 1, '', 1, 1,now(),now());
INSERT INTO `menu_items` VALUES (4, '红烧鲈鱼', 45.00, '新鲜鲈鱼红烧制作，肉质鲜美，营养丰富', '鲁菜', 1, '咸鲜微甜', '鲈鱼,生抽,老抽,冰糖,葱姜', '红烧', 0, '鱼类', 1, 1,now(),now());
INSERT INTO `menu_items` VALUES (5, '蒜蓉西兰花', 12.00, '新鲜西兰花配蒜蓉，营养丰富，适合减肥人群', '素食', 0, '蒜香清淡', '西兰花,大蒜,橄榄油', '蒸炒', 1, '无过敏源', 1,0,now(),now());


drop table IF EXISTS reservation_order;
CREATE TABLE reservation_order(
  id int AUTO_INCREMENT COMMENT '预订单ID，主键自增',
  num_people int NOT NULL COMMENT '客人人数',
  num_children int NOT NULL COMMENT '儿童人数',
  arrival_time datetime NOT NULL COMMENT '到达时间',
  seat_preference varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '座位偏好',
  main_dish_preference varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '主菜偏好',
  other_comments text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '其他备注需求',
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '预订单表' ROW_FORMAT = Dynamic;
