// es6
let vm = new Vue({
    el:"#app",
    //修改vue读取变量的方法
    delimiters:["[[","]]"],
    data:{
        //v-model
        username:"",
        password:"",
        password2:"",
        mobile:"",
        image_code:"",
        image_code_url:"",
        sms_code:"",
        sms_code_tip:"获取短信验证码",
        allow:"",
        send_flag:false,
        //v-show
        error_username:false,
        error_password:false,
        error_password2:false,
        error_mobile:false,
        error_image_code:false,
        error_sms_code:false,
        error_allow:false,
        //提示信息
        error_username_username:"",
        error_password_message:"",
        error_password2_message:"",
        error_mobile_message:"",
        error_image_code_message:"",
        error_sms_code_message:"",
        error_allow_message:"",
    },
    mounted(){
        this.generate_image_code();
    },
    methods:{
        //用户名
        check_username(){
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            if(re.test(this.username)){
                this.error_username = false
                this.error_username_message = ""
            }else{
                this.error_username = true
                this.error_username_message = "请输入5到20位的用户名"
            }
            //判断用户名是否已经存在 axios 前后端交互
            if(this.username = false){
                let url = "users/username/"+ this.username + "/count/"
                axios.get(url,{
                    responseType:"json"
                })
                //请求成功通过
                .then(response=>{
                    if(response.data.count == 1){
                        this.error_username = true
                        this.error_username_message = "用户名已经存在"
                    }else{
                        this.error_username = false
                        this.error_username_message = ""
                    }

                })
                //请求失败
                .catch(error=>{
                    console.log(error.response)
                })
            }
        },
        //密码
        check_password(){
            let re = /^[a-zA-Z0-9_-]{8,20}$/;
            if(re.test(this.password)){
                this.error_password = false
                this.error_password_message = ""
            }else{
                this.error_password = true
                this.error_password_message = "请输入8到20位的密码"
            }
        },
        //确认密码
        check_password2(){
          if(this.password2 == this.password){
            this.error_password2 = false
            this.error_password2_message = ""
          }else{
            this.error_password2 = true
            this.error_password2 = "两次密码输入不一致"
          }
        },
        //电话号码
        check_mobile(){
            let re = /^1[23456789]\d{9}$/;
            if(re.test(this.mobile)){
                this.error_mobile = false
                this.error_mobile_message = ""
            }else{
                this.error_mobile = true
                this.error_mobile_message = "请输入正确格式的手机号码"
            }
            let url = "users/mobile/"+ this.mobile + "/count/"
            axios.get(url,{
                responseType:"json"
            })
            .then(response=>{
                if(response.data.count == 1){
                    this.error_mobile = true
                    this.error_mobile_message = "手机号码已经存在"

                }else{
                    this.error_mobile = false
                    this.error_mobile_message = ""
                }
            })
            .catch(error=>{
                console.log(error.response)
            })
        },
        //图形验证码
        generate_image_code(){
            this.uuid = generateUUID()
            this.image_code_url = "/image_code/" + this.uuid + "/"
        },
        check_image_code(){
            if(image_code.length == 4){
                this.error_image_code = false
                this.error_image_code_message = ""
            }else{
                this.error_image_code = true
                this.error_image_code_message = "请输入四位的图形验证码"
            }
        },
        //短信验证码
        //发送短信验证码
        send_sms_code(){
            //当已经发送了的时候 再次点击没有作用
            if(this.send_flag == true){
                return;
            }else{
                this.send_flag = true
            }
            this.check_mobile()
            this.check_image_code()
            if(this.error_image_code == true || this.error.mobile == true){
                return;
            }
            let url = "/sms_code/"+ this.mobile + "/?image_code=" + this.image_code + "&uuid=" + this.uuid
            axios.get(url,{
                responseType:"json"
            })
            .then(response=>{
                let num = 60
                if(response.data.code == "1"){
                    let t = setInterval(()=>{
                        if(num == 1){
                            clearInterval(t)
                            this.sms_code_tip = "获取验证码"
                            this.generate_image_code()
                            this.send_flag = false
                        }else{
                            num -= 1
                            this.sms_code_tip = num + "秒"
                        }
                    },1000)
                }else{
                    if(response.data.code == "0"){
                        this.error_image_code_message = response.data.error_message
                        this.error_image_code = true
                    }
                    this.send_flag = false
                }

            })
            .catch(error=>{
                console.log(error.response)
                this.send_flag = false
            })
        },
        check_sms_code(){
            if(this.sms_code.length != 6){
                this.error_sms_code = true
                this.error_sms_code_message = "短信验证码长度不对"
                this.send_flag = false
            }else{
                this.error_sms_code = false
                this.error_sms_code_message = ""
            }
        },
        check_allow(){
            if(!this.allow){
                this.error_allow = true
                this.error_allow_message = "请勾选用户协议"
            }else{
                this.error_allow = false
            }
        }

        on_submit(){
            if(this.error_username == true || this.error_password == true || this.error_mobile == true || this.error_image_code == true){
                window.event.returnValue = false
            }
        }


    }
})