var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        token: sessionStorage.token || localStorage.token,

        addresses: [],      // 当前登录用户的地址列表
        user_id: 0,         // 当前登录用户的id
        default_address_id: '',     // 当前登录用户的默认地址的id
    },

    mounted: function(){
        // 请求当前登录用户的所有的地址
         axios.get('http://127.0.0.1:8000/addresses/',{
                headers: {
                    'Authorization': 'JWT ' + this.token
                }
             }
         ).then(response=>{
                this.addresses=response.data.addresses;
                this.default_address_id=response.data.default_address_id
            }).catch(error=> {
             alert('获取失败')
         })
       
    },

    methods: {
        // 设置默认地址
        set_default: function(){
            if (!this.default_address_id) {
                alert('请先选择默认地址');
                return
            }
			//发送请求
           
        },

        // 删除地址
        delete_address: function(address_id) {
             axios.delete('http://127.0.0.1:8000/addresses/'+address_id+"/",{
                headers: {
                    'Authorization': 'JWT ' + this.token
                }
             }
         ).then(response=>{
               location.reload()
            }).catch(error=> {
             alert('删除失败')
         })
            
        }
    }
});