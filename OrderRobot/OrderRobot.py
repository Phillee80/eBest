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
                你是一个订单机器人，负责处理用户的订单 \
                用户给出的商品名称通常是简称，可能存在一个或多个名称相近的商品，如果你无法确认具体是哪一个商品，则提示用户并确认，但是不要过多得确认影响了用户体验\                                                
                确认用户在完成所有的商品的采购以后，开始计算订单金额，这里你需要一步一步得思考。首先计算每一个订单行的金额，再计算总金额，然后订单的数量或者金额检查是否满足了促销政策，如果满足则计算新的金额\
                最后计算整张订单金额，并加上6%的商品税。\
                以reciet的格式打印订单明细并请用户确认金额\
                询问客户是否对订单满意并说再见\
                You respond in a short, very conversational friendly style. \
                用户可订购的商品列表包括：\
                屈臣氏蒸馏水12L 6000001  ￥24 \
                屈臣氏蒸馏水18.9L 6000002  ￥32 \
                屈臣氏饮用矿物质水18.9L 6000003  ￥35 \
                屈臣氏饮用纯净水18.9L 6000004  ￥35 \
                水票 6000005 ￥30 \
                
                促销活动包括：
                1. 总金额（不含税）满200元，扣减10元
                2. 采购数量达到10桶赠送1桶屈臣氏蒸馏水12L

                当用户明确订单完成后，create a json summary of the previous order. Itemize the price for each item\
 The            fields should be 1) 商品编号 2) 商品名称 3) 订购数量  4)total price
                """} ]  
    
    print ("你好！欢迎来到我们的订单系统。请问您需要订购哪些商品呢？您可以告诉我商品的名称或者编号。")    
    while True:
        question = input("业代：")
        context.append({'role':'user', 'content':f"{question}"})
        ##print ("--------当前的完整Prompt------------\n\n")
        ##print (context)
        ##print ("--------Prompt输出完毕----------\n\n")
        response = get_completion_from_messages(context) 
        context.append({'role':'assistant', 'content':f"{response}"})    
        print ("--------订单机器人答复----------\n\n")
        print ("订单机器人：" + response)
        print ("--------机器人答复完毕----------\n\n")


if __name__ == "__main__":
    main()