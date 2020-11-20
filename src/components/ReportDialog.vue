<template>
  <div id="report_dialog">
    <div class="dialog_head">
      <div class="title">
        <span class="name">装箱单查询</span>
      </div>
      <ul class="dialog_icons">
        <li>
          <i class="fa fa-close" aria-hidden="true" @click="closeDialog()"></i>
        </li>
      </ul>
    </div>
    <div class="buttons-wrap">
      <el-button-group>
        <el-button plain icon="el-icon-arrow-left" size="mini" @click="back()"></el-button>
        <el-button plain size="mini"><i class="el-icon-arrow-right el-icon--right" @click="back()"></i></el-button>
      </el-button-group>
      <el-button-group>
        <el-button plain icon="el-icon-download"  size="mini" @click="toExcel()"></el-button>
        <el-button plain icon="el-icon-search"  size="mini" @click="isFilter = true"></el-button>
      </el-button-group>
    </div>
    <el-row :gutter="20" style="padding: 0 5px;">
      <el-col :span="12">
        <el-date-picker
          size="mini"
          v-model="date"
          value-format="yyyy/MM/dd"
          type="daterange"
          unlink-panels
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期">
        </el-date-picker>
      </el-col>
      <el-col :span="8">
        <el-input v-model="form_code" placeholder="销售单单号" size="mini"></el-input>
      </el-col>
      <el-col :span="4">
        <el-button icon="el-icon-refresh" @click="mid_search()" size="mini" circle type="primary" plain></el-button>
      </el-col>
    </el-row>
    <div class="mid-container">
      <table class="table" v-if="!isLine">
        <thead>
          <tr>
            <th :width="th.width" v-for="th in titles">{{ th.name }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row_data in formdata"  @dblclick="toLines(row_data.code, 1, 1)">

            <td>{{ row_data.form_code }}</td>
            <td>{{ row_data.code }}</td>
            <td>{{ row_data.partner_name }}</td>
            <td>{{ row_data.store_name }}</td>
            <td>{{ row_data.box_count }}/{{ row_data.box_id }}</td>
            <td>{{ row_data.created_at }}</td>
            <td>{{ row_data.created_user }}</td>
            <td>{{ row_data.executed_at }}</td>
            <td>{{ row_data.executed_user }}</td>
          </tr>
        </tbody>
      </table>
      <table class="table line-table" v-else>
        <thead>
        <tr>
          <th>装箱单号</th>
          <th>商品名称</th>
          <th>装箱数量</th>
        </tr>
        </thead>
        <tbody>
          <tr v-for="row_data in linesFormData">
            <td>{{ row_data.code }}</td>
            <td>{{ row_data.product_name }}</td>
            <td>{{ row_data.packing_quantity }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="footer-container">
      <div class="pagination">
        <el-pagination
          background
          @current-change="handleCurrentChange"
          layout="total, prev, pager, next"
          :total="total">
        </el-pagination>
      </div>
    </div>
      <!-- 过滤对话框 -->
  <div class="filter-container" v-show="isFilter">
    <div class="filter">
      <div class="dialog_head">
        <div class="title">
          <span class="name">过滤条件</span>
        </div>
        <ul class="dialog_icons">
          <li>
            <i class="fa fa-close" aria-hidden="true" @click="isFilter = false"></i>
          </li>
        </ul>
      </div>
      <div class="dialog_content">
        <form name="filterform" id="filterform" @submit.prevent="mid_search()">
          <div class="editor-label">
            <label>开始时间：</label>
              <el-date-picker
                v-model="date2.start_date"
                type="date"
                value-format="yyyy/MM/dd"
                placeholder="选择开始时间">
              </el-date-picker>
          </div>
          <div class="editor-label">
            <label>结束时间：</label>
              <el-date-picker
                v-model="date2.end_date"
                type="date"
                value-format="yyyy/MM/dd"
                placeholder="选择结束时间">
              </el-date-picker>
          </div>
          <div class="editor-label">
            <label>销售单号：</label>
            <el-input v-model="form_code"></el-input>
          </div>
          <div class="editor-label">
            <label>装箱单号：</label>
            <el-input v-model="code"></el-input>
          </div>
          <div class="btn-label">
            <el-button round  size="mini" @click="mid_search()">确定</el-button>
            <el-button round  size="mini" @click="isFilter = false">取消</el-button>
          </div>
        </form>
      </div>
    </div>
  </div>
    <!-- 过滤对话框  -  结束 -->
  </div>
</template>

<script>
import mixin from '../js/mixins.js'
export default {
  name: 'ReportDialog', // 装箱单报表
  mixins: [mixin],
  data () {
    return {
      tmpName: 'ReportDialog',
      store_name: [],
      isFilter: false,
      isSearched: false,
      formdata: [], // 表格
      linesFormData: [], // 明细表格
      titles: [
        {
          name: '出库单号',
          width: '10%'
        }, {
          name: '装箱单号',
          width: '10%'
        }, {
          name: '商业伙伴',
          width: '10%'
        }, {
          name: '仓库',
          width: '10%'
        }, {
          name: '箱数/箱号',
          width: '10%'
        }, {
          name: '创建时间',
          width: '10%'
        }, {
          name: '创建用户',
          width: '10%'
        }, {
          name: '执行时间',
          width: '10%'
        }, {
          name: '执行用户',
          width: '10%'
        }
      ],
      date: [],
      date2: {
        start_date: '',
        end_date: ''
      },
      form_code: '', // 销售单单号
      code: '', // 装箱单单号
      total: '',
      totalMain: '',
      totalSub: '',
      limit: 10,
      disableBack: true,
      timeout: null,
      isLine: false // 帮助判断在哪一层
    }
  },
  mounted () { // 设置默认时间 月初和当日
    let time = []
    var date = new Date()
    var year = date.getFullYear()
    var month = date.getMonth() + 1
    var today = date.getDate()
    time[0] = `${year}/${month}/1`
    time[1] = `${year}/${month}/${today}`
    this.date = time
    this.date2.start_date = time[0]
    this.date2.end_date = time[1]
  },
  watch: {
    date: {
      handler (n, o) { // 两处时间绑定
        this.date2.start_date = n[0]
        this.date2.end_date = n[1]
      }
    },
    date2: {
      handler (n, o) {
        this.date = [n.start_date, n.end_date]
      },
      deep: true
    }
  },
  methods: {
    toLines (code, index, start) { // 页码和装箱单号
      start = (start - 1) * this.limit || 0
      if (start < 0) {
        start = 0
      }
      let params = { // 过滤
        start_date: this.date[0],
        end_date: this.date[1] ? this.getNewDay(this.date[1], 1) : '',
        form_code: this.form_code,
        code: code || this.code,
        start: start,
        limit: this.limit
      }
      this.$axios({
        url: `/api/packing_reports?action=packing_line`,
        params: params
      }).then(res => {
        if (res.state === 1) {
          this.disableBack = false
          this.totalSub = res.total
          this.total = res.total
          this.linesFormData = res.results
          this.isLine = true
          this.code = res.code
          return
        }
        return alert(res.errmsg)
      })
    },
    handleCurrentChange (val) {
      if (this.isLine) {
        this.toLines(null, null, val)
      }
      this.mid_search(Number(val))
    },
    mid_search (start) {
      this.isSearched = true
      start = (start - 1) * this.limit || 0
      let params = { // 过滤
        start_date: this.date[0],
        end_date: this.date[1] ? this.getNewDay(this.date[1], 1) : '',
        form_code: this.form_code,
        code: this.code || '',
        start: start,
        limit: this.limit
      }
      let url = ''
      if (this.isLine) {
        return this.toLines(this.code, 1, 0)
      } else {
        url = `/api/packing_reports?action=packing_list`
      }
      this.$axios({
        url: url,
        params: params
      }).then(res => {
        if (res.state === 1) {
          this.totalMain = res.total // 主表数量
          this.total = res.total
          this.formdata = res.result
          return
        }
        return alert(res.errmsg)
      })
      this.isFilter = false
    },
    back () { // 从明细返回主表
      if (!this.disableBack) { this.isLine = !this.isLine }
      if (!this.isLine) { // 如果是主表，左下角的数量充值未主表数量
        this.total = this.totalMain
      } else {
        this.total = this.totalSub
      }
    },
    toExcel () {
      if (!this.isSearched) { return alert('请先进行查询') }
      let url = ''
      if (this.isLine) {
        url = `/api/packing_reports?action=packing_line`
      } else {
        url = `/api/packing_reports?action=packing_list`
      }
      let params = { // 过滤
        start_date: this.date[0] || '',
        end_date: this.date[1] ? this.getNewDay(this.date[1], 1) : '',
        code: this.code,
        format: 'excel'
      }
      this.$axios({ // 下载Excel
        url: url,
        responseType: 'blob',
        params: params
      }).then(data => {
        if (data.state === 0) {
          return alert(data.errmsg)
        }
        let url = window.URL.createObjectURL(new Blob([data]))
        let link = document.createElement('a')
        link.style.display = 'none'
        link.href = url
        let title = ''
        this.isLine ? title = '装箱单商品明细.xlsx' : title = '装箱单.xlsx'
        link.setAttribute('download', title)
        document.body.appendChild(link)
        link.click()
      })
    }
  }
}
</script>

<style scoped lang="less">
@import "../style/base.less";
  #report_dialog{
    overflow: hidden;
    box-shadow: 0 0 10px;
    border-radius: 5px;
    background: #fff;
    width: 800px;
    height: 500px;
    position: absolute;
    left: 50%;
    margin-left: -400px;
    top: 50%;
    margin-top: -250px;
    .dialog_head {
      line-height: 33px;
      padding: 0 10px;
      .name {
        padding-left: 10px;
      }
    }
    .buttons-wrap{
      padding: 5px 5px 3px 5px;
    }
    .mid-container{
      padding: 5px;
      text-align: center;
      overflow-x: auto;
      height: 330px;
      .table{
        width: 1200px;
        border-collapse: collapse;
        tr {
          border: 1px solid #f1f1f1;
          transition: all ease 0.3s;
          &:hover {
            border-bottom:1px solid #b6d3f7;
          }
        }
        thead {
          background-color: #f1f1f1;
        }
      }
      .line-table {
        width: 100%;
      }
    }
    .footer-container{
      .el-pagination {
        margin-top: 5px;
      }
    }
    .block{
      display: inline-block;
      width: 170px;
    }
  }
  .editor-label input {
    width: 175px;
    height: 28px;
    line-height: 28px;
    position: relative;
  }
  .filter-container{
  position: absolute;
  width: 360px;
  height: 300px;
  left: 50%;
  top: 50%;
  margin-left: -180px;
  margin-top: -150px;
  box-shadow: 0 0 10px;
  border-radius: 5px;
  background: #fff;
}
</style>
