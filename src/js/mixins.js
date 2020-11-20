let mixins = {
  data () {
    return {
    }
  },
  mounted () {},
  methods: {
    // 日期加上天数得到新的日期
    // dateTemp 需要参加计算的日期，days要添加的天数，返回新的日期，日期格式：YYYY/MM/DD
    getNewDay (dateTemp, days) {
      var dateTemp = dateTemp.split('/')
      var nDate = new Date(dateTemp[1] + '/' + dateTemp[2] + '/' + dateTemp[0]) // 转换为MM/DD/YYYY格式
      var millSeconds = Math.abs(nDate) + (days * 24 * 60 * 60 * 1000)
      var rDate = new Date(millSeconds)
      var year = rDate.getFullYear()
      var month = rDate.getMonth() + 1
      if (month < 10) month = '0' + month
      var date = rDate.getDate()
      if (date < 10) date = '0' + date
      return (year + '/' + month + '/' + date)
    },
    sum (arr) {
      return eval(arr.join('+'))
    },
    diglogTrigger (name, boolean) {
      this['show_' + name] = boolean
    },
    closeDialog () {
      this.index = 0 // 关闭后再次打开是第一箱
      eventBus.$emit('f-close-dialog', this.tmpName, false)
    },
    printPDF (url, token) {
      this.$axios({
        url: url,
        method: 'POST',
        responseType: 'arraybuffer',
        params: {
          Token: token
        }
      }).then(function (data) {
        if (data.state == 0) {
          return alert(data.errmsg)
        }
        let file = new Blob([data], { type: 'application/pdf' }) // 使用Blob将PDF Stream 转换为file
        let fileUrl = window.URL.createObjectURL(file)
        window.open(fileUrl)
      })
    }
  }
}
export default mixins
