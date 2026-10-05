import asyncio
import math
import time

import aiohttp

TARGET_URL = "http://localhost:8000/classify"
CONCURRENT_REQUESTS = 50
TOTAL_REQUESTS = 100
TIMEOUT_SLA = 2.0


async def send_request(session: aiohttp.ClientSession, req_id: int):
    payload = {"text": f"Tin nhắn thử nghiệm benchmark hiệu năng request thứ {req_id}"}
    start = time.time()
    try:
        async with session.post(
            TARGET_URL, json=payload, timeout=aiohttp.ClientTimeout(total=5.0)
        ) as resp:
            elapsed = time.time() - start
            if resp.status == 200:
                data = await resp.json()
                return {
                    "status": "success",
                    "latency": elapsed,
                    "score": data.get("score"),
                }
            else:
                return {"status": "http_error", "latency": elapsed, "code": resp.status}
    except asyncio.TimeoutError:
        elapsed = time.time() - start
        return {"status": "timeout", "latency": elapsed}
    except Exception as e:
        elapsed = time.time() - start
        return {"status": "error", "latency": elapsed, "error": str(e)}


def calculate_percentile(sorted_list, percentile):
    if not sorted_list:
        return 0.0
    index = (percentile / 100.0) * (len(sorted_list) - 1)
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return sorted_list[int(index)]
    weight = index - lower
    return sorted_list[lower] * (1 - weight) + sorted_list[upper] * weight


async def run_benchmark():
    print("=" * 70)
    print(f"🚀 BẮT ĐẦU BENCHMARK HIỆU NĂNG INFERENCE SERVICE (SLA < {TIMEOUT_SLA}s)")
    print(f"- Target URL: {TARGET_URL}")
    print(f"- Concurrent Requests: {CONCURRENT_REQUESTS}")
    print(f"- Total Requests: {TOTAL_REQUESTS}")
    print("=" * 70)

    async with aiohttp.ClientSession() as session:
        tasks = [send_request(session, i) for i in range(TOTAL_REQUESTS)]
        start_all = time.time()
        results = await asyncio.gather(*tasks)
        total_duration = time.time() - start_all

    latencies = [r["latency"] for r in results if r["status"] == "success"]
    success_count = sum(1 for r in results if r["status"] == "success")
    timeout_count = sum(
        1 for r in results if r["latency"] > TIMEOUT_SLA or r["status"] == "timeout"
    )
    error_count = sum(1 for r in results if r["status"] in ("error", "http_error"))

    latencies.sort()
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    p95 = calculate_percentile(latencies, 95)
    p99 = calculate_percentile(latencies, 99)
    success_rate = (success_count / TOTAL_REQUESTS) * 100.0
    rps = TOTAL_REQUESTS / total_duration if total_duration > 0 else 0.0

    print("\n📊 KẾT QUẢ PHÂN TÍCH HIỆU NĂNG:")
    print("-" * 50)
    print(f"• Tổng thời gian thực thi : {total_duration:.2f} giây")
    print(f"• Tốc độ xử lý (Throughput): {rps:.2f} requests/sec")
    print(
        f"• Tỷ lệ thành công         : {success_rate:.2f}% ({success_count}/{TOTAL_REQUESTS})"
    )
    print(f"• Số request quá SLA > 2s   : {timeout_count}")
    print(f"• Lỗi kết nối/HTTP          : {error_count}")
    print(
        f"• Latency trung bình (Avg) : {avg_latency * 1000:.2f} ms ({avg_latency:.4f}s)"
    )
    print(f"• Latency Percentile 95th  : {p95 * 1000:.2f} ms ({p95:.4f}s)")
    print(f"• Latency Percentile 99th  : {p99 * 1000:.2f} ms ({p99:.4f}s)")
    print("-" * 50)

    # Criteria check
    pass_sla = p95 < TIMEOUT_SLA and timeout_count == 0 and success_rate >= 95.0
    if pass_sla:
        print(
            "✅ ĐÁNH GIÁ KẾT QUẢ: [PASS] - Hệ thống đáp ứng hoàn hảo tiêu chuẩn SLA < 2s!"
        )
    else:
        print(
            "❌ ĐÁNH GIÁ KẾT QUẢ: [FAIL] - Độ trễ vượt ngưỡng SLA hoặc tỷ lệ lỗi cao!"
        )
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_benchmark())
