<template>
  <div id="app">
    <div class="input-code editor-label">
      <label style="width: auto;">短单号：</label>
      <el-input style="width: 52%" v-model.trim="short_no" autofocus resize @focus="short_no = ''" @keyup.enter.native="short_no_search()"></el-input>
      <i class="fa fa-search fa-lg" aria-hidden="true" @click="short_no_search()" ></i>
    </div>
    <div id="tab1">
      <el-button plain  type="primary" @click="c_scanBtn()">装箱及打印</el-button>
      <el-button plain  type="primary" @click="c_boxCheckBtn()">装箱单查询</el-button>
    </div>
    <div class="order-form">
      <form class="border_radius clearfix billform" id="mainTable">
        <div class="editor-label" v-for="inputItem in list">
          <label :style="inputItem.nameStyle">{{ inputItem.name }}：</label>
          <el-date-picker
            v-if="inputItem.datePicker"
            v-model="inputItem.value"
            :style="inputItem.style"
            type="date"
            value-format="yyyy/MM/dd"
            placeholder="选择日期">
          </el-date-picker>
          <el-input
            v-else
            v-model.trim="inputItem.value"
            :class="inputItem.class"
            :readonly="inputItem.readonly">
          </el-input>
        </div>
        <div class="form-btn">
          <el-button type="primary" size="medium" @click.prevent="onSave()">保存</el-button>
        </div>
      </form>
    </div>
    <ReportDialog v-if="show_ReportDialog" /> <!-- 装箱单查询与其他组件没有通信 用if方便关闭实现清空数据 -->
    <BillDialog v-show="show_BillDialog" :res="res" :token="token" ref="BillDialog" />
  </div>
</template>

<script>
import ReportDialog from './components/ReportDialog'
import BillDialog from './components/BillDialog'
import mixin from './js/mixins.js'

export default {
  name: 'App',
  mixins: [mixin],
  components: {
    ReportDialog, // 装箱单报表
    BillDialog // 装箱及打印
  },
  props: ['token'],
  mounted () {
    eventBus.$on('changeisExecuted', bool => {
      if (bool == true) {
        this.res.status = 6
      }
    })
    eventBus.$on('f-close-dialog', (name, boolean) => {
      this.diglogTrigger(name, boolean)
    })
    eventBus.$on('openFilter', data => {
      this.show_Filter = data
    })
  },
  data () {
    return {
      show_WorkspacefilterDialog: false,
      show_PartnerDialog: false,
      show_BillDialog: false,
      show_ReportDialog: false,
      show_Filter: false,
      isSearched: false,
      res: {},
      container: [],
      short_no: '',
      list: [
        {
          name: '单号',
          key: 'form_code',
          value: '',
          readonly: true
        },
        {
          name: '仓库',
          key: 'store_name',
          value: '',
          readonly: true
        },
        {
          name: '商业伙伴',
          key: 'partner_name',
          value: '',
          readonly: true
        },
        {
          name: '联系人',
          key: 'contactor',
          value: ''
        },
        {
          name: '联系电话',
          key: 'phone',
          value: ''
        },
        {
          name: '手机号',
          key: 'mobile_phone',
          value: ''
        },
        {
          name: '数量',
          key: 'total_quantity',
          value: '',
          readonly: true
        },
        {
          name: '京东订单单号',
          key: 'order_id',
          value: '',
          readonly: true
        },
        {
          name: 'TC预约号',
          key: 'tc_code',
          value: '',
          nameStyle: 'font-weight: bold;'
        },
        {
          name: 'TC预约送货日期',
          key: 'tc_date',
          value: '',
          style: 'display: inline;',
          nameStyle: 'font-weight: bold;',
          datePicker: true
        },
        {
          name: '目的城市',
          key: 'des',
          value: '',
          readonly: true
        },
        {
          name: '目的仓库',
          key: 'store',
          value: '',
          readonly: true
        },
        {
          name: '省',
          key: 'province',
          value: ''
        },
        {
          name: '市',
          key: 'city',
          value: ''
        },
        {
          name: '区',
          key: 'district',
          value: ''
        },
        {
          name: '街道',
          key: 'town',
          value: ''
        },
        {
          name: '详细地址',
          key: 'shipping_address',
          value: '',
          class: 'shipping_address'
        },
        {
          name: '备注',
          key: 'memo',
          value: '',
          class: 'memo'
        }
      ],
      id: ''
    }
  },
  methods: {
    clear () {
      this.short_no = ''
    },
    c_scanBtn () {
      if (this.short_no == '') return alert('请输入短单号查询')
      if (this.res.status !== 6) {
        this.onSave()
      } else {
        this.$refs.BillDialog._open(this.res.id)
      }
      this.diglogTrigger('BillDialog', true)
    },
    c_boxCheckBtn () {
      // 装箱单报表
      this.diglogTrigger('ReportDialog', true)
    },
    upDate (res) {
      if (res.state === 1) {
        this.res = res
        this.container = this.list
        for (let i = 0, len = this.container.length; i < len; i++) {
          for (var keyName in res) {
            if (this.container[i].key == keyName) { this.container[i]['value'] = res[keyName] }
          }
        }

        this.list = this.container
        this.container = []
      } else alert(res.errmsg)
    },
    onSave () {
      let data = {}
      let config = {}
      for (let i = 0, len = this.list.length; i < len; i++) {
        let keyName = this.list[i].key
        data[keyName] = this.list[i].value
      }
      data = Object.assign({}, this.res, data) // 更新res
      if (this.res.id != null) {
        config = {
          url: `/api/packing_lists/${this.res.id}`,
          method: 'PUT',
          data: data
        }
      } else {
        config = {
          url: `/api/packing_lists`,
          method: 'POST',
          data: data
        }
      }
      this.$axios(config).then(res => {
        if (res.state === 1) {
          this.upDate(res)
          this.res = res
          this.$refs.BillDialog._open(res.id)
          this.$message({
            type: 'success',
            message: '保存成功!'
          })
        } else {
          return alert(res.errmsg)
        }
      })
    },
    async short_no_search () {
      if (!this.short_no) {
        return alert('请输入短单号')
      } else {
        const Result = await this.$axios({
          url: '/api/packing_lists',
          params: {
            short_no: this.short_no
          }
        })
        if (!Result.state) {
          alert(Result.errmsg)
          return
        } else {
          this.isSearched = true
          this.upDate(Result)
          eventBus.$emit('getSatus', Result.status, Result.form_code)
        }
        await this.c_scanBtn() // 搜索正常的单子自动打开装箱单录入弹窗
      }
    }
  }
}
</script>

<style lang="less">
@import "./style/base.less"; // 通用样式
#app {
  font-family: "Microsoft YaHei", "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  .order-form{
    background-color: floralwhite;
  }
}
.editor-label .el-input{
  width: 60%;
}
#mainTable {
  .editor-label:nth-of-type(17), .editor-label:nth-of-type(18) {
    width: 660px;
  }
  .shipping_address, .memo{
    width: 491px;
    input{
      width: 100%;
    }
  }
}
.editor-label>div{
  display: inline;
}
.order-form .editor-label label {
  width: 117px;
}
.order-form .el-input__icon {
  line-height: normal;
}
</style>
