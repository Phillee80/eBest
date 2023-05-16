Page({
  data: {
    inputText: '',
    responses: [],
    loading: false,
    inputFocus: false,
  },

  onInputChange: function (e) {
    this.setData({
      inputText: e.detail.value,
    });
  },

  generateSessionId() {
    return new Date().getTime().toString(16);
  },

  onCopyTap: function (e) {
    const textToCopy = e.currentTarget.dataset.text;
    wx.setClipboardData({
      data: textToCopy,
      success: function () {
        wx.showToast({
          title: '已复制到剪贴板',
          icon: 'success',
          duration: 1500,
        });
      },
    });
  },
  
  onDeleteTap: function (e) {
    const indexToDelete = e.currentTarget.dataset.index;
    const newResponses = [...this.data.responses];
    newResponses.splice(indexToDelete, 1);
    this.setData({
      responses: newResponses,
    });
  },
  

  requestApi: function (queryText) {
    wx.showLoading({
      title: '正在努力思考',
    })
    console.log("requestApi 被调用");
    const url = "https://gpt.ebestmobile.net/api/chatgpt/v2";
    const payload = {
            "question": queryText
  };

    wx.request({
      url,
      method: "POST",
      data: payload,
      header: {
        "content-type": "application/json",
      },
      success: (response) => {
        console.log("请求成功：", response);
        const result = `eBestChat答曰：\n${response.data.data.answer.result}\n\n`;

        this.setData({
          responses: [...this.data.responses, result],
          loading: false,
        });
        console.log("查询", this.data.responses);
        // const queryButton = this.selectComponent("#queryButton");
        // queryButton.disabled = false;
      },
      fail: (error) => {
        console.log("请求失败：", error);
    
        let errorMessage = "未知错误，请稍后重试";
        if (error.errMsg.includes("timeout")) {
          errorMessage = "我这会忙得冒烟，请稍后重试";
        } else if (error.errMsg.includes("server")) {
          errorMessage = "API挂了，客官请稍后重试";
        } else if (error.errMsg.includes("network")) {
          errorMessage = "网络连接错误，请检查您的网络设置";
        }else {
          errorMessage = "遇到了火星错误，请联系客服Linda小姐姐";
        }
    
        this.setData({
          loading: false,
        });
    
        // 添加弹出提示
        wx.showModal({
          title: '提示',
          content: errorMessage,
          showCancel: false, // 不显示取消按钮
          confirmText: '确定', // 确定按钮的文本
          confirmColor: '#3CC51F', // 确定按钮的颜色
        });
    },
      complete:()=>{
        wx.hideLoading({
          success: (res) => {},
        })
      }
    });
  },

  onClearClick: function () {
    this.setData({
      inputText: '',
    });
  },

  

  onQueryClick: function () {
    console.log("提问按钮被点击");
    const queryText = this.data.inputText;
    const inputText = this.selectComponent("#inputText");
  
    console.log("提问按钮被点击",queryText);
    if (!queryText) return; 
  
    this.requestApi(queryText);
}

})