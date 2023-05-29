import os
import openai

openai.api_key  = "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"



def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, 
    )
    return response.choices[0].message["content"]
 
def main():
    context = [ {'role':'system', 'content':"""
                                                你是一个订单机器人，负责处理零售门店的订单 \
                                                如果用户给出的商品名称存在多个名称相近的商品，则提示用户并询问具体订购得是哪一款商品\
                                                确认用户在完成所有的商品的采购以后，再检查订单计算整张订单金额，并加上6%的商品税。\
                                                以reciet的格式打印订单明细并请用户确认金额\
                                                询问客户是否对订单满意并说再见\
                                                You respond in a short, very conversational friendly style. \

                                                用户可订购的商品列表包括：\
                                                巧克力威化32条装 12379596  ￥30 \
                                                花生威化32条装 12379595  ￥28 \
                                                能恩1号900g 12361474  ￥50 \
                                                燕麦米粉25g 12310764  ￥30 \
                                                咖啡伴侣瓶装200g 9121005 ￥15 \
                                                咖啡伴侣瓶装100g 9121802 ￥20 \
                                                摩卡10(5x21g) 12368771 ￥25  \
                                                1+2原味微研磨7条 12361489 ￥20 \

                                                促销活动包括：
                                                1. 总金额（不含税）满200元，扣减10元
                                                2. 购买10箱燕麦米粉25g，赠送1箱燕麦米粉25g
                                                """} ]  # accumulate messages
    
    print ("你好！欢迎来到我们的订单系统。请问您需要订购哪些商品呢？您可以告诉我商品的名称或者编号。")    
    while True:
        question = input("业代：")
        context.append({'role':'user', 'content':f"{question}"})
        print ("--------当前的完整Prompt------------\n\n")
        print (context)
        print ("--------Prompt输出完毕----------\n\n")
        response = get_completion_from_messages(context) 
        context.append({'role':'assistant', 'content':f"{response}"})    
        print ("--------订单机器人答复----------\n\n")
        print ("订单机器人：" + response)
        print ("--------机器人答复完毕----------\n\n")


if __name__ == "__main__":
    main()