
装箱单模块说明文档
==============================

前后端交互规则
==========================

后台成功时返回{"state": 1, ...}, 后台报错时会返回{"state": 0, "errmsg": "错误信息"}.

数据库结构
==========================

### 1. set\_of_books 账套信息

	* id 
	* set_of_book 账套号
	* name 供应商名称
	* address 地址

### 2. packing_lists   装箱单

    * id
    * code 单号
    * box_count 箱数
    * form_name 生成装箱单的单据名称
    * form_code 生成装箱单的单据code
    * form_id 生成装箱单的单据id
    * partner_name 商业伙伴名称
    * store_name 仓库名称
    * contactor 联系人
    * phone 电话
    * mobile_phone 手机号
    * province 省
    * city 市
    * district 区
    * town 街道
    * shipping_address 地址
    * total_quantity 总数量
    * memo 备注
    * form_created_at 销售单创建时间
    * status 单据状态
    * created_user 创建用户
    * created_at 创建时间
    * updated_at 更新时间
    * updated_user 更新用户
    * executed_user 执行用户
    * executed_at 执行时间
    * order_id 京东订单号
    * des 目的城市
    * store 目的仓库
    * set_of_book 账套号


### 3. packing\_list_lines  装箱单明细

    * id
    * packing_list_id 装箱单id
    * code 装箱单明细code
    * total_quantity 总数量
    * set_of_book 账套号


### 4. product_lines 产品明细

    * id
    * packing_list_line_id 装箱单明细id
    * product_id 产品id
    * product_name 产品名称
    * product_code 商品编码
    * quantity 数量
    * packing_quantity 装箱数量
    * set_of_book 账套号

接口说明
==============

### 1. /api/access_token  get 获取token,调用其他接口时需要在headers中传递该token

	* 传递参数 params
	
		* url c8地址
		* set_of_book 账套号
		* user_name 用户名称
	* headers
	
		* Token c8的令牌
	
	* 返回数据
	
		* 成功时:{"state": 1, "token": 令牌}
		* 出错时:{"state": 0, "errmsg": 错误信息}

### 2. /api/packing_lists get 通过短单号查找销售单

	* 传递参数:
	
	    * short_no 短号
	   
	* headers
		* Token 令牌
	
	* 返回数据 json格式
	
	    * state 状态,用于前台分辨后台是否成功执行(0,1)
	    * id 装箱单id
	    * code 装箱单code
	    * form_name 生成装箱单的单据名称
	    * form_code 生成装箱单的单据code
	    * form_id 生成装箱单的单据id
	    * partner_name 商业伙伴名称
	    * store_name 仓库名称
	    * contactor 联系人
	    * phone 联系电话
	    * mobile_phone 手机号
	    * province 省
	    * city 市
	    * district 区
	    * town 街道
	    * shipping_address 详细地址
	    * total_quantity 总数量
	    * memo 备注
	    * form_created_at 销售单创建时间
	    * status 状态
	    * created_at 创建时间
	    * created_user 创建用户
	    * updated_at 更新时间
    	* updated_user 更新用户
	    * executed_at 执行时间
	    * executed_user 执行用户
	    * box_count 装箱数量
	    * order_id 京东订单号
	    * des 目的城市
	    * store 目的仓库
	    * sale_order_lines 销售单明细(如果没有生成装箱单时返回)
	    	* product_id 商品id
	    	* product_name 商品名称
	    	* product_code 商品编码
	    	* quantity 数量

### 3. /api/packing_lists/[id] get 通过装箱单id获取装箱单

	* 传递参数
	
		* 无
	
	* headers:
	
		* Token 令牌

	* 返回数据 json格式

		* state 状态,用于前台分辨后台是否成功(0,1)
	    * id 装箱单id
	    * code 装箱单code
	    * form_name 生成装箱单的单据名称
	    * form_code 生成装箱单的单据code
	    * form_id 生成装箱单的单据id
	    * partner_name 商业伙伴名称
	    * store_name 仓库名称
	    * contactor 联系人
	    * phone 联系电话
	    * mobile_phone 手机号
	    * province 省
	    * city 市
	    * district 区
	    * town 街道
	    * shipping_address 详细地址
	    * total_quantity 总数量
	    * memo 备注
	    * form_created_at 销售单创建时间
	    * status 状态
	    * created_at 创建时间
	    * created_user 创建用户
	    * updated_at 更新时间
    	* updated_user 更新用户
	    * executed_at 执行时间
	    * executed_user 执行用户
	    * box_count 装箱数量
	    * order_id 京东订单号
	    * des 目的城市
	    * store 目的仓库

### 4. /api/packing_lists  post 创建装箱单

	* 传递参数:  json格式
	
	    * form_name 生成装箱单的单据名称
	    * form_code 生成装箱单的单据code
	    * form_id 生成装箱单的单据id
	    * partner_name 商业伙伴名称
	    * store_name 仓库名称
	    * contactor 联系人
	    * phone 联系电话
	    * mobile_phone 手机号
	    * province 省
	    * city 市
	    * district 区
	    * town 街道
	    * shipping_address 详细地址
	    * total_quantity 总数量
	    * memo 备注
	    * form_created_at 销售单创建时间
	    * order_id 京东订单号
	    * des 目的城市
	    * store 目的仓库
	    * packing_list_lines 装箱单明细(非必要, 与sale_order_lines二选一) json数组
	
	        * product_lines 商品明细, json数组
	
	            * product_id 商品id
	            * product_name 商品名称
	            * product_code 商品编码
	            * quantity 数量
	            * packing_quantity 装箱数量
	
	
	    * sale_order_lines 销售单单明细(非必要, 与packing_list_lines二选一) json数组
	
	        * product_id 商品id
	        * product_name 商品名称
	        * product_code 商品编码
	        * quantity 数量
	
	* headers

		* Token 令牌
	
	* 返回数据 json格式
	
	    * state 状态,用于前台分辨后台是否成功(0,1)
	    * id 装箱单id
	    * code 装箱单code
	    * form_name 生成装箱单的单据名称
	    * form_code 生成装箱单的单据code
	    * form_id 生成装箱单的单据id
	    * partner_name 商业伙伴名称
	    * store_name 仓库名称
	    * contactor 联系人
	    * phone 联系电话
	    * mobile_phone 手机号
	    * province 省
	    * city 市
	    * district 区
	    * town 街道
	    * shipping_address 详细地址
	    * total_quantity 总数量
	    * memo 备注
	    * form_created_at 销售单创建时间
	    * status 状态
	    * created_at 创建时间
	    * created_user 创建用户
	    * updated_at 更新时间
    	* updated_user 更新用户
	    * executed_at 执行时间
	    * executed_user 执行用户
	    * box_count 装箱数量
	    * order_id 京东订单号
	    * des 目的城市
	    * store 目的仓库

### 5. /api/packing_lists/[id]  put 更新装箱单

	* 传递参数 json格式
	
	    * contactor 联系人
	    * phone 联系电话
	    * mobile_phone 手机号
	    * province 省
	    * city 市
	    * district 区
	    * town 街道
	    * shipping_address 详细地址
	    * memo 备注
	    * packing_list_lines 装箱单明细(非必要) 
	
	        * id 装箱单明细id(有id表示是已存在的明细,不传时为新增的明细)
	        * product_lines json数组
	
	            * id 商品明细id(如果传了装箱单明细id时必传)
	            * product_id 商品id
	            * product_name 商品名称
	            * product_name 商品编码
	            * quantity 数量
	            * packing_quantity 打包数量
	
	* 返回数据 json格式
	
	    * state 状态,用于前台分辨后台是否成功(0,1)
	    * id 装箱单id
	    * code 装箱单code
	    * form_name 生成装箱单的单据名称
	    * form_code 生成装箱单的单据code
	    * form_id 生成装箱单的单据id
	    * partner_name 商业伙伴名称
	    * store_name 仓库名称
	    * contactor 联系人
	    * phone 联系电话
	    * mobile_phone 手机号
	    * province 省
	    * city 市
	    * district 区
	    * town 街道
	    * shipping_address 详细地址
	    * total_quantity 总数量
	    * memo 备注
	    * form_created_at 销售单创建时间
	    * status 状态
	    * created_at 创建时间
	    * created_user 创建用户
	    * updated_at 更新时间
    	* updated_user 更新用户
	    * executed_at 执行时间
	    * executed_user 执行用户
	    * box_count 装箱数量
	    * order_id 京东订单号
	    * des 目的城市
	    * store 目的仓库


### 6. /api/packing_lists/[id]?action=execute  get
	* 传递参数 params
	    
	    无
	    
	* headers
	
		* Token 令牌
	
	* 返回数据 json格式
	
	    * state 状态,用于前台分辨后台是否成功(0,1)
	    * id 装箱单id
	    * code 装箱单code
	    * form_name 生成装箱单的单据名称
	    * form_code 生成装箱单的单据code
	    * form_id 生成装箱单的单据id
	    * partner_name 商业伙伴名称
	    * store_name 仓库名称
	    * contactor 联系人
	    * phone 联系电话
	    * mobile_phone 手机号
	    * province 省
	    * city 市
	    * district 区
	    * town 街道
	    * shipping_address 详细地址
	    * total_quantity 总数量
	    * memo 备注
	    * form_created_at 销售单创建时间
	    * status 状态
	    * created_at 创建时间
	    * created_user 创建用户
	    * executed_at 执行时间
	    * executed_user 执行用户
	    * box_count 装箱数量
	    * order_id 京东订单号
	    * des 目的城市
	    * store 目的仓库


### 7. /api/packing_lists/[id]?action=print post 打印单据
	
	* 传递参数 json格式

		* form_name 打印类型, form_name=packing_list时,打印送货单; form_name=tag时,打印箱标.
		* Token 令牌
	
	* 说明:
		
		* 只有执行完成的装箱费才能打印送货单
		* 打印箱标时,如果装箱单未执行,需要传递box_count参数


### 8. /api/packing\_lists/[id]/packing\_list_lines get 获取装箱单明细

	* 传递参数 params

		无
		
	* headers

		* Token 令牌

	* 返回数据 json格式
	
	    * state 状态,用于前台分辨后台是否成功(0,1)
	    * total_quantity 总数量
	    * status 装箱单状态
	    * packing_list_lines json数组
	
	        * id 装箱单明细id
	        * code 装箱单明细id
	        * packing_list_id 装箱单id
	        * total_quantity 明细装箱总数量
	        * product_lines 产品明细 json数组
	
	            * id 产品明细id
	            * product_id 产品id
	            * product_name 产品名称
	            * product_code 产品编码
	            * quantity 数量
	            * packing_quantity 打包数量
	            * packing_list_line_id 装箱单明细id

报表
=====

第一级
=======

###1. /api/packing\_reports?action=packing_list  get
	* 可传参数:
	    
	    * start_date 开始时间(执行时间)
	    * end_date 结束时间(执行时间)
	    * form_code 销售单单号
	    * code 装箱单单号
	    * start, limit 分页必传
	    * format 下载报表时传format=excel

	* headers

		* Token 令牌
	
	* 返回数据 json数组
	
	    * created_at 创建时间
	    * created_user 创建用户
	    * executed_at 执行时间
	    * executed_user 执行用户
	    * form_code 出库单号
	    * code 装箱单号
	    * box_count 总箱数

第二级
=======

###2. /api/packing\_reports?action=packing_line  get
	* 可传参数:
	
	    * start_date 开始时间(执行时间)
	    * end_date 结束时间(执行时间)
	    * form_code 出库单单号
	    * code 装箱单号
	    * start, limit 分页必传
	    * format 下载报表时传format=excel
	
	* headers

		* Token 令牌

	
	* 返回数据 json
	    
	    * total 总条数
	    * results 数据
	
	        * code 装箱单明细单号
	        * product_name 商品名称
	        * packing_quantity 装箱数量