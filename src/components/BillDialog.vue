<template>
  <div id="bill_dialog" class="dialog bill_widget">
    <div class="dialog_head">
      <div class="title">
        <span class="name">装箱单录入</span>
      </div>
      <ul class="dialog_icons">
        <li>
          <i class="fa fa-close" aria-hidden="true" @click="closeDialog()"></i>
        </li>
      </ul>
    </div>
    <div class="dialog_content" style="height:400px">
      <div id="container" class="barcodeContainer">
        <div id="closeMain">
          <div id="billContainer">
            <div class="tabwidget">
              <div class="editor-label" style="width:400px;">
                <label>产品码：</label>
                <el-input
                  v-model.trim="barcode"
                  clearable @keyup.enter.native="searchSKU()"
                  id="SKU"
                  autofocus="isFocus"
                  @focus="barcode = ''">
                </el-input>
                <i class="fa fa-search fa-lg search" id="searchBarcode" @click="searchSKU()"></i>
              </div>
              <div class="editor-label status">
                <label>状态：</label>
                <el-tag type="success" v-if="res.status == 6"><i class="el-icon-success"></i>&nbsp;已完成</el-tag>
                <el-tag type="danger" v-else><i class="el-icon-warning"></i>&nbsp;未完成</el-tag>
              </div>
              <div class="mid-container">
                <div class="left">
                  <div class="left-title">装箱单序号</div>
                  <ul>
                    <li v-for="(item, index1) in packing_list_lines" @click="showRow(index1)" :class="index1 == index? 'active':''">第{{ index1 + 1 }}箱</li>
                  </ul>
                  <div class="left-btn">
                    <div @click="aBox()"><i class="fa fa-plus-square" aria-hidden="true"></i> 新增</div>
                    <div @click="mBox()"><i class="fa fa-minus-square" aria-hidden="true"></i> 删除</div>
                  </div>
                </div>
                <div class="right">
                  <table class="fake-head">
                    <thead>
                      <tr>
                        <th v-for="til in titles" :style="til.style">{{ til.name }}</th>
                      </tr>
                    </thead>
                  </table>
                  <table border="1" v-for="(box, index) in packing_list_lines" v-show="isThisBox(index)">
                    <thead>
                      <tr style="height: 40px">
                        <th v-for="til in titles" :style="til.style">{{ til.name }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <!-- 这里的class name id 等大多是为了方便获取元素 -->
                      <tr v-for="(product, index2) in box.product_lines">
                        <td style="text-align:left;">【{{ product.barcode }}】：{{ product.name }}</td>
                        <td style="text-align:left;" :title="product.product_name">{{ product.product_name }}</td>
                        <td>{{ product.product_code }}</td>
                        <td :class="['quantity' + index2, boldNumber]" :data-item="product.quantity">{{ product.quantity }}</td>
                        <!-- 剩余数量 -->
                        <td class ="boldNumber" :name="'unpacked' + index2"></td>
                        <td>
                          <input type="number"
                                   :name="product.barcode"
                                   :class="['packed' + index2, boldNumber]"
                                   :data-item="product.packing_quantity"
                                   v-model.number="product.packing_quantity"
                                   min="0"
                                   step="1"
                                   @keyup.enter="moveFocus()"
                                   @focus="product.packing_quantity = ''" />
                        </td>
                        <td v-if="index2 == 0" :rowspan="rowspan">
                          <input class="weight boldNumber" v-model="box.weight" @focus="box.weight = ''" style="border: none;outline:none;text-align:center;">
                        </td>
                        <td v-if="index2 == 0" :rowspan="rowspan">
                          <input class="weight boldNumber" v-model="box.volume" @focus="box.volume = ''" :title="box.volume" style="border: none;outline:none;text-align:center;width:100%">
                        </td>
                      </tr>
                      <tr style="height: 30px">
                        <td colspan="3">合计</td>
                        <td class="boldNumber">{{ total_quantity }}</td>
                        <td class="boldNumber">{{ total_rest }}</td>
                        <td class="boldNumber">{{ total_packed }}</td>
                        <td class="boldNumber">{{ total_weight }}</td>
                        <td class="boldNumber">-</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              <div class="table_btn">
                <el-button type="primary" size="medium" @click="c_weighBtn()"  :disabled="isExecuted">称重</el-button>
                <el-button type="primary" size="medium" @click="c_saveBoxButton()" :disabled="isExecuted">保存本箱</el-button>
                <el-button type="primary" size="medium" @click="c_executeBtn()" :disabled="isExecuted">执行</el-button>
                <el-button type="primary" size="medium" @click="c_batchPrintBtn()" :disabled="!isExecuted">打印装箱单</el-button>
                <el-button type="primary" size="medium" @click="c_goodsBtn()" :disabled="!isExecuted">打印箱标</el-button>
                <el-button type="primary" size="medium" @click="c_saveButton()" :disabled="isExecuted">保存整单</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import mixin from '../js/mixins.js'
export default {
  name: 'BillDialog', // 装箱单
  mixins: [mixin],
  data () {
    return {
      barcode: '',
      boldNumber: 'boldNumber',
      tmpName: 'BillDialog',
      titles: [
        {
          name: '商品名及产品码',
          style: 'width:20%;'
        },
        {
          name: '京东商品名称',
          style: 'width:25%;'
        }, {
          name: '京东商品编码',
          style: 'width:8.3%'
        }, {
          name: '总数量',
          style: 'width:8.3%'
        }, {
          name: '剩余数量',
          style: 'width:8.3%'
        }, {
          name: '装箱数量',
          style: 'width:8.3%'
        }, {
          name: '重量(kg)',
          style: 'width:8.3%'
        }, {
          name: '体积',
          style: 'width:13.3%'
        }
      ],
      packing_list_lines: [],
      t_res: [],
      index: 0,
      total_quantity: '',
      total_weight: '',
      total_packed: '',
      product_packed: '', // 单个货品装箱数量
      rowspan: '',
      isExecuted: false,
      t_id: ''
    }
  },
  props: ['res', 'token'],
  mounted () {
    eventBus.$on('getSatus', (status, formCode) => {
      if (status === 6) { // 执行完的不能点前三个按钮
        this.isExecuted = true
      } else {
        this.isExecuted = false
      }
      this.res.form_code = formCode
    })
    this.showRow()
  },
  methods: {
    c_goodsBtn () {
      if (!this.isExecuted) {
        return alert('请先执行再打印')
      }
      let id = this.res.id
      let token = this.token
      let url = `/api/packing_lists/${id}?action=print&form_name=tag`
      this.printPDF(url, token)
    },
    moveFocus () {
      document.getElementById('SKU').focus()
    },
    rest () {
      let proAmount = this.packing_list_lines[0].product_lines.length
      this.rowspan = proAmount
      for (let i = 0; i < proAmount; i++) {
        let quantity = document.getElementsByClassName('quantity' + i)[0]
        let unpacked = document.getElementsByName('unpacked' + i)
        let packed = Array.prototype.slice.call(document.getElementsByClassName('packed' + i))
        let quantityNum = Number(quantity.getAttribute('data-item'))
        let empty = []
        let packedsum = 0
        for (let j = 0; j < packed.length; j++) {
          empty.push(Number(packed[j].value))
          packedsum = this.sum(empty)
        }
        let outcome = quantityNum - packedsum
        let arr = Array.prototype.slice.call(unpacked)
        for (let x = 0; x < arr.length; x++) {
          arr[x].innerHTML = outcome
          if (outcome < 0) { // 在这里控制剩余数量不要在watch里监控
            return alert('剩余数量不能小于0')
          }

          if (outcome === 0) {
            arr[x].parentNode.classList.remove('whiteBgc')
            arr[x].parentNode.classList.add('greenBgc')
          } else {
            arr[x].parentNode.classList.remove('greenBgc')
            arr[x].parentNode.classList.add('whiteBgc')
          }
          this.packing_list_lines[x].product_lines[i].outcome = outcome
        }
      }
    },
    c_weighBtn () {
      document.getElementsByClassName('weight')[this.index].focus()
    },
    searchSKU () {
      let SKU = this.barcode
      let pro = this.packing_list_lines[this.index].product_lines
      for (let i = 0; i < pro.length; i++) { // 当前箱子
        if (SKU == pro[i].barcode) {
          return document.getElementsByName(SKU)[this.index].focus()
        }
      }
      this.$message.error('未查询到产品码!')
    },
    aBox () { // 新增箱子
      if (this.res.status === 6) {
        this.$message({
          type: 'warning',
          message: '已执行的装箱单不能修改!'
        })
        return
      }
      if (this.total_rest === 0) {
        this.$message({
          type: 'warning',
          message: '剩余数量已为0'
        })
        return
      }
      if (!this.saveBeforeAdd()) {
        return alert('装箱数量全部为0，请检查')
      }
      let len = this.packing_list_lines.length
      let lastBox = JSON.parse(JSON.stringify(this.packing_list_lines[len - 1]))
      // 清空一些信息
      for (let i = 0; i < lastBox.product_lines.length; i++) {
        lastBox.product_lines[i].packing_quantity = 0
        lastBox.product_lines[i].id = ''
      }
      lastBox.id = ''
      lastBox.code = ''
      lastBox.weight = 0

      this.packing_list_lines.push(lastBox)
      this.index = this.packing_list_lines.length - 1
      this.moveFocus()
    },
    mBox () { // 删除第N个箱子
      if (this.res.status === 6) {
        this.$message({
          type: 'warning',
          message: '已执行的装箱单不能修改!'
        })
        return
      }
      if (!confirm(`确定要删除第${this.index + 1}箱？`)) return
      if (!this.packing_list_lines[this.index].id) { // 没有保存的箱子可以直接删除
        this.packing_list_lines.splice(this.index, 1)
        this.showRow()
        return
      }
      this.$axios({
        url: `/api/packing_lists/${this.res.id}/packing_list_lines/${this.packing_list_lines[this.index].id}`,
        method: 'DELETE'
      }).then(res=> {
        if (res.state === 1) {
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
          this.packing_list_lines.splice(this.index, 1)
          this.showRow()
          return
        }
        return alert(res.errmsg)
      })
    },
    isThisBox (index) {
      if (index == this.index) { return true }
    },
    c_saveBoxButton () { // 保存本箱 就是点新增自动保存本箱的功能 现在再单独做一个按钮
      this.saveBeforeAdd()
    },
    async c_saveButton () {
      if (!confirm(`确定已经完成装箱，将保存整箱？`)) return
      var id = this.res.id, data, empty
      empty = this.packing_list_lines
      for (let i = 0, len = empty.length; i < len; i++) { // 返回给后端时 装箱的''要再改回0
        for (let j = 0, len2 = empty[i].product_lines.length; j < len2; j++) {
          empty[i].product_lines[j].packing_quantity = empty[i].product_lines[j].packing_quantity || 0
        }
      }
      data = {
        packing_list_lines: empty
      }
      await this.$axios.put(`/api/packing_lists/${id}`, data).then(res => {
        if (res.state === 1) {
          this.$message({
            type: 'success',
            message: '此箱保存成功!'
          })
          return
        }
        return alert(res.errmsg)
      })
    },
    c_executeBtn () {
      let id = this.res.id
      this.$axios.get(`/api/packing_lists/${id}?action=execute`).then(res => {
        if (res.state === 1) {
          this.$message({
            type: 'success',
            message: '执行成功!'
          })
          this.isExecuted = true
          eventBus.$emit('changeisExecuted', this.isExecuted)
          return
        }
        return alert(res.errmsg)
      })
    },
    saveBeforeAdd () { // 新增时自动保存前一箱
      let id = this.res.id
      let config = {}
      let thisBox = this.packing_list_lines[this.index]
      let lineId = thisBox.id || ''
      let _box = thisBox // 打包数量的''改为0 再传给后端
      let isAllow = false
      for (let i = 0, len = _box.product_lines.length; i < len; i++) {
        _box.product_lines[i].packing_quantity = _box.product_lines[i].packing_quantity || 0
        if (!_box.product_lines[i].packing_quantity) {
          _box.product_lines[i].packing_quantity = 0
        }else{
          isAllow = true
        }
      }
      if (!isAllow) return false
      if (typeof lineId !== 'number') {
        config = {
          url: `/api/packing_lists/${id}/packing_list_lines`,
          method: 'POST',
          data: {
            packing_list_lines: _box
          }
        }
        return this.$axios(config).then(res=> {
          if (res.state === 1) {
            this.packing_list_lines[this.index].id = res.id
            for (let j = 0, len = res.product_lines.length; j < len; j ++) {
              this.packing_list_lines[this.index].product_lines[j].id = res.product_lines[j].id
            }
            this.$message({
              type: 'success',
              message: `保存成功!`
            })
            return
          }
          return alert(res.errmsg)
        })
      } else {
        config = {
          url: `/api/packing_lists/${id}/packing_list_lines/${lineId}`,
          method: 'PUT',
          data: {
            packing_list_lines: _box
          }
        }
        return this.$axios(config).then(res=> {
          if (res.state === 1) {
            this.$message({
              type: 'success',
              message: `保存成功!`
            })
            return
          }
          return alert(res.errmsg)
        })
      }
    },
    c_batchPrintBtn () { // 打印整个装箱单
      if (this.isExecuted == false) return alert('请先执行')
      let id = this.res.id
      let token = this.token
      let url = `/api/packing_lists/${id}?action=print&form_name=packing_list`
      this.printPDF(url, token)
    },
    showRow (index) {
      index = index || 0
      this.index = index
    },
    _open (id) {
      this.$axios({
        url: `/api/packing_lists/${id}/packing_list_lines`
      }).then(res => {
        if (!res.state) return alert(res.errmsg)
        this.t_res = res
        this.total_quantity = res.total_quantity
        this.packing_list_lines = res.packing_list_lines
        this.$nextTick(() => {
          this.rest()
        })
        this.moveFocus()
      })
    }
  },
  computed: {
    total_rest () {
      return this.total_quantity - this.total_packed
    }
  },
  watch: {
    packing_list_lines: { // 装箱单和重量变化时重新计算
      handler (n, o) {
        let sum = 0
        let weight = 0
        let box = this.packing_list_lines
        for (let i = 0, len = box.length; i < len; i++) {
          for (let j = 0, len2 = box[i].product_lines.length; j < len2; j++) {
            let packingQuantity = box[i].product_lines[j].packing_quantity
            sum += Number(packingQuantity)
            box[i].product_lines[j].packing_quantity = packingQuantity || '' // 因为要求为0时不显示
          }
          weight += Number(box[i].weight)
        }
        this.total_packed = sum
        this.total_weight = weight
        this.$nextTick(() => {
          this.rest()
        })
        return n
      },
      deep: true
    }
  }
}
</script>

<style scoped lang="less">
@import "../style/base.less";
.greenBgc {
  background-color: #cafbf0;
}
.whiteBgc {
  background-color: #fff;
}
.status {
  float: right;
  margin-right: 200px;
}
.mid-container {
  height: 270px;
  overflow: hidden;
  .left {
    border: 1px solid #c5c5c5;
    text-align: center;
    width: 15%;
    float: left;
    margin: 0 1%;
    .left-btn {
      cursor: pointer;
      height: 30px;
      overflow: hidden;
      line-height: 30px;
      & > div {
        float: left;
        width: 50%;
        &:active {
          line-height: 36px;
        }
      }
    }
    ul {
      border: 1px solid #f1f1f1;
      height: 180px;
      overflow-y: auto;
      li {
        cursor: pointer;
        border-bottom: 1px solid #f1f1f1;
        transition: all ease 0.3s;
        &:hover {
          background-color:ivory;
        }
      }
    }
  }
  .right {
    float: right;
    width: 83%;
    height: 235px;
    overflow-y: auto;
    border-bottom: 1px solid #c5c5c5;
    table {
      text-align: center;
      min-height: 235px;
      border-collapse: collapse;
      tbody tr {
        height: 36px;
        border: 1px solid #c5c5c5;
        transition: all ease 0.3s;
        &:hover {
          color:dodgerblue;
        }
        input {
          width: 60px;
        }
      }
      thead {
        background-color: #f1f1f1;
      }
    }
    .fake-head{
      position: absolute;
      width: 798px;
      thead{
        tr{
          height: 40px;
        }
      }
    }
  }
}
.boldNumber{
  font-size: 20px;
  font-weight: bold;
  text-align: center;
  &:hover{
    color:dodgerblue;
  }
}
table{table-layout: fixed;}
td{word-break: break-all; word-wrap:break-word;}
</style>
