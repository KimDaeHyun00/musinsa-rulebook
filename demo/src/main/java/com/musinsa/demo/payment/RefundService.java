package com.musinsa.demo.payment;

// 개발자 B가 작성 — donghyun이 등록한 팀 규칙(money-bigdecimal-not-double)을 모르고 double 사용
public class RefundService {

    public double calculateRefundAmount(Order order) {
        double refundAmount = 0.0;
        for (Item item : order.getItems()) {
            refundAmount += item.getPrice() * item.getQuantity();
        }
        return refundAmount;
    }
}
