// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import 'font-awesome/less/font-awesome.less'
import Vue from 'vue'
import App from './App'
import axios from 'axios'
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import mixin from './js/mixins'

Vue.config.productionTip = false
Vue.prototype.$axios = axios
Vue.use(ElementUI)
/* eslint-disable no-new */
function ready (infoData) {
  window.eventBus = new Vue()
  var vm = new Vue({
    el: '#app',
    components: {
      App
    },
    mixins: [mixin],
    template: '<App :token="token"/>',
    data: {
      token: '',
      partner: '',
      store: ''
    },
    mounted () {
      this.getToken()
      this.interceptors()
    },
    methods: {
      getToken () {
        let referrerUrl = document.referrer
        let url = referrerUrl.slice(0, referrerUrl.indexOf('/static'))
        let userInfo = infoData.user
        this.$axios({
          url: '/api/access_token',
          params: {
            url: url,
            set_of_book: userInfo.set_of_book,
            user_name: userInfo.name
          },
          headers: {
            'Token': userInfo.token
          }
        }).then(res => {
          if (res.data.state === 1) {
            this.token = res.data.token
          }
          else alert(res.data.errmsg)
        }).catch(err => {
          console.log(err)
        })
      },
      interceptors () {
        this.$axios.interceptors.request.use(config => {
          config.headers['Token'] = this.token
          this.$loading({
            text: '加载中...',
            spinner: 'el-icon-loading',
            background: 'rgba(255, 255, 255, 0.9)'
          });
          return config
        }, error => {
          return Promise.reject(error)
        })
        this.$axios.interceptors.response.use(response => {
          this.$loading({
            text: '加载中...',
            background: 'rgba(255, 255, 255, 0.9)'
          }).close();
          return response.data
        }, error => {
          return Promise.reject(error.response)
        })
      }
    }
  })
}

// event 参数中有 data 属性，就是父窗口发送过来的数据
window.addEventListener('message', function (event) {
  ready(JSON.parse(event.data))
}, false)
