package com.musinsa.demo.delivery;

import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

// 데모용 안티패턴: 배송사 타입별 if/else 분기 + 핫패스 단일계층 Redis 의존
@Service
public class DeliveryTrackerService {

    private final RedisTemplate<String, Object> redisTemplate;

    public DeliveryTrackerService(RedisTemplate<String, Object> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    public TrackingInfo track(Order order) {
        if (order.getCarrierType() == CarrierType.CJ) {
            return trackCj(order);
        } else if (order.getCarrierType() == CarrierType.HANJIN) {
            return trackHanjin(order);
        } else if (order.getCarrierType() == CarrierType.LOTTE) {
            return trackLotte(order);
        }
        throw new IllegalArgumentException("unknown carrier");
    }

    private TrackingInfo trackCj(Order o) { return readCache(o); }
    private TrackingInfo trackHanjin(Order o) { return readCache(o); }
    private TrackingInfo trackLotte(Order o) { return readCache(o); }

    private TrackingInfo readCache(Order o) {
        return (TrackingInfo) redisTemplate.opsForValue().get("track:" + o.getId());
    }
}
