azureuser@slm-ft-t4:~/Ramakrishna$ cat /tmp/motor_demo_logs/mcp.log
2026-09-24 09:11:57,892 | INFO | No auth config provided, skipping auth setup
2026-09-24 09:11:57,893 | INFO | MCP HTTP server listening at /mcp
2026-09-24 09:11:57,895 | INFO | No auth config provided, skipping auth setup
2026-09-24 09:11:57,895 | INFO | MCP HTTP server listening at /mcp
/home/azureuser/Ramakrishna/claims-SLM-Finetune/MotorTriageAgents/MCP/main.py:85: DeprecationWarning: 
        on_event is deprecated, use lifespan event handlers instead.

        Read more about it in the
        [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
        
  @app.on_event("startup")
INFO:     Started server process [6991]
INFO:     Waiting for application startup.
2026-09-24 09:11:58,167 | INFO | init_db: all tables created / verified OK
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8500 (Press CTRL+C to quit)
INFO:     127.0.0.1:55732 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:41110 - "GET /api/v1/slm_triage/poll HTTP/1.1" 200 OK
2026-09-24 09:12:19,244 | INFO | StreamableHTTP session manager started
2026-09-24 09:12:19,244 | INFO | StreamableHTTP session manager is running
2026-09-24 09:12:19,343 | INFO | Created new transport with session ID: ebf8d1be7b014d4b9fcae8f9a822d4af
INFO:     127.0.0.1:41114 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:41114 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:12:19,349 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:41138 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:12:19,351 | INFO | Terminating session: ebf8d1be7b014d4b9fcae8f9a822d4af
INFO:     127.0.0.1:41138 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:41124 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:12:21,015 | INFO | Created new transport with session ID: 432af048b98f4aab8eb59aab78a7a1b1
2026-09-24 09:12:21,015 | INFO | Created new transport with session ID: 6884514ecdc943dba84b5318c5963059
INFO:     127.0.0.1:41140 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:41144 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:41140 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:41144 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:12:21,026 | INFO | Processing request of type CallToolRequest
2026-09-24 09:12:21,027 | INFO | Processing request of type CallToolRequest
2026-09-24 09:12:21,339 | INFO | Loading Qwen SLM pipeline (base + adapters A/B/C, 4-bit)…
2026-09-24 09:12:21,822 | INFO | HTTP Request: GET http://apiserver/claim/CLM-MOT-MUF7AI8V "HTTP/1.1 200 OK"
INFO:     127.0.0.1:41182 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:12:21,826 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:41182 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:12:21,828 | INFO | Terminating session: 432af048b98f4aab8eb59aab78a7a1b1
INFO:     127.0.0.1:41182 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:41152 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
Loading weights: 100%|██████████| 625/625 [00:01<00:00, 445.37it/s]
2026-09-24 09:12:30,622 | INFO | Qwen SLM pipeline ready
loaded base + 3 adapters (a, b, c) from /home/azureuser/Ramakrishna/claims-SLM-Finetune/models/Qwen3-VL-2B-Instruct
INFO:     127.0.0.1:35630 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:12:56,214 | INFO |   [A] b71b9f20-6a43-4fa8-809f-cb9f397acfe2.pdf -> repair_estimate (22 fields)
INFO:     127.0.0.1:57520 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:53826 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:13:44,750 | INFO |   [A] f5dfbe28-4713-4c43-b5d9-c7a3968fd8ce.pdf -> policy_data_coverage (26 fields)
INFO:     127.0.0.1:42458 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:14:15,589 | INFO |   [A] 45463239-768c-4cc1-8aab-ba165de16a99.pdf -> fnol (29 fields)
2026-09-24 09:14:19,267 | INFO | Created new transport with session ID: f2690695395a4630afd77cf9ed11a4a8
INFO:     127.0.0.1:47904 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:47904 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:14:19,273 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:47924 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:14:19,275 | INFO | Terminating session: f2690695395a4630afd77cf9ed11a4a8
INFO:     127.0.0.1:47924 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:47914 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:14:21,102 | INFO | Created new transport with session ID: 17f10e50694a4ea0be00b106f660b297
2026-09-24 09:14:21,102 | INFO | Created new transport with session ID: 117d1584e7bc4bc1875941af1b33159c
INFO:     127.0.0.1:47936 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:47944 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:47936 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:47944 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:14:21,111 | INFO | Processing request of type CallToolRequest
2026-09-24 09:14:21,113 | INFO | Processing request of type CallToolRequest
2026-09-24 09:14:21,488 | INFO | HTTP Request: GET http://apiserver/claim/CLM-MOT-MUFA5VG0 "HTTP/1.1 200 OK"
INFO:     127.0.0.1:47968 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:14:21,491 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:47968 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:14:21,499 | INFO | Terminating session: 17f10e50694a4ea0be00b106f660b297
INFO:     127.0.0.1:47968 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:47948 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:51934 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:14:51,488 | INFO |   [A] 048dfdf3-6df8-4fa5-8c5a-2ab7491957de.pdf -> driver_statement (17 fields)
INFO:     127.0.0.1:47372 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:15:34,345 | INFO |   [A] fe449832-077d-42a4-985b-6bc94f8cde8f.pdf -> repair_estimate (22 fields)
INFO:     127.0.0.1:37294 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:53150 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:16:19,290 | INFO | Created new transport with session ID: d698b4bc82fd40f0a256b82b9f8c838e
INFO:     127.0.0.1:40262 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:40262 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:16:19,297 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:40274 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:19,299 | INFO | Terminating session: d698b4bc82fd40f0a256b82b9f8c838e
INFO:     127.0.0.1:40274 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:40268 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:21,121 | INFO | Created new transport with session ID: efd7c409ef5f4e9998deda100cd11bca
2026-09-24 09:16:21,121 | INFO | Created new transport with session ID: 0b054aec9cec4ea8b495221c5246ec7c
INFO:     127.0.0.1:40288 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:40298 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:40288 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:40298 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:16:21,131 | INFO | Processing request of type CallToolRequest
2026-09-24 09:16:21,133 | INFO | Processing request of type CallToolRequest
2026-09-24 09:16:21,435 | INFO | HTTP Request: GET http://apiserver/claim/CLM-MOT-MUFAP0ND "HTTP/1.1 200 OK"
INFO:     127.0.0.1:40328 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:21,437 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:40328 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:21,439 | INFO | Terminating session: efd7c409ef5f4e9998deda100cd11bca
INFO:     127.0.0.1:40328 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:40304 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:57946 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:16:41,669 | INFO | StreamableHTTP session manager started
2026-09-24 09:16:41,669 | INFO | StreamableHTTP session manager is running
2026-09-24 09:16:41,769 | INFO | Created new transport with session ID: 92f9f34785d547888668d24a879e4193
INFO:     127.0.0.1:57952 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:57952 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:16:41,777 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:57980 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:41,778 | INFO | Terminating session: 92f9f34785d547888668d24a879e4193
INFO:     127.0.0.1:57980 - "DELETE /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:57968 - "GET /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:43,943 | INFO | Created new transport with session ID: ad88be85819448ff9b287ce46da64e65
2026-09-24 09:16:43,943 | INFO | Created new transport with session ID: 7bb4236103f14c06a2e1a102be4c11e7
INFO:     127.0.0.1:57984 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:57990 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:57984 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:57990 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:16:43,955 | INFO | Processing request of type CallToolRequest
2026-09-24 09:16:43,957 | INFO | Processing request of type CallToolRequest
2026-09-24 09:16:44,273 | INFO | HTTP Request: GET http://apiserver/claim/CLM-MOT-MUFBI8H3 "HTTP/1.1 200 OK"
INFO:     127.0.0.1:58036 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:44,275 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:58036 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:44,277 | INFO | Terminating session: ad88be85819448ff9b287ce46da64e65
INFO:     127.0.0.1:58036 - "DELETE /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:58006 - "GET /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:44,525 | INFO | intake_validation claim=CLM-MOT-MUFBI8H3 outcome=pass completeness=100% status=Triage Pending
2026-09-24 09:16:44,526 | INFO | HTTP Request: POST http://apiserver/run/CLM-MOT-MUFBI8H3 "HTTP/1.1 200 OK"
INFO:     127.0.0.1:58048 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:44,529 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:58048 - "POST /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
2026-09-24 09:16:44,530 | INFO | Terminating session: 7bb4236103f14c06a2e1a102be4c11e7
INFO:     127.0.0.1:58048 - "DELETE /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:58022 - "GET /api/v1/intake_validation/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:60308 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:17:44,230 | INFO |   [A] a7f2a460-f0a0-40c9-8e6a-0dc151e8e8ea.pdf -> repair_estimate (22 fields)
INFO:     127.0.0.1:41866 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:17:52,712 | INFO |   [A] 62d382e3-988c-4561-b1c2-173ba9ea16e4.pdf -> policy_data_coverage (26 fields)
INFO:     127.0.0.1:51518 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:46302 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:58788 - "GET /api/v1/slm_triage/poll HTTP/1.1" 200 OK
2026-09-24 09:18:49,577 | INFO | Created new transport with session ID: b3f94f9787dc41fb85da197799d3d854
INFO:     127.0.0.1:58796 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:58796 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:18:49,585 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:58816 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:18:49,587 | INFO | Terminating session: b3f94f9787dc41fb85da197799d3d854
INFO:     127.0.0.1:58816 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:58804 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:18:52,291 | INFO | Created new transport with session ID: bd8a456169c9455f91c3d1c0e28f06ec
2026-09-24 09:18:52,291 | INFO | Created new transport with session ID: 60b87a6d87d942039fb0de9b25de7ee2
INFO:     127.0.0.1:58826 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:58834 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:58826 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:58834 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:18:52,303 | INFO | Processing request of type CallToolRequest
2026-09-24 09:18:52,305 | INFO | Processing request of type CallToolRequest
2026-09-24 09:18:52,608 | INFO | HTTP Request: GET http://apiserver/claim/CLM-MOT-MUF7AI8V "HTTP/1.1 200 OK"
INFO:     127.0.0.1:58870 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:18:52,611 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:58870 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:18:52,613 | INFO | Terminating session: bd8a456169c9455f91c3d1c0e28f06ec
INFO:     127.0.0.1:58870 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:58848 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:60284 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:38380 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:19:59,941 | INFO |   [A] 81f3de9a-39f2-4996-a2cc-d7f87d0e252f.pdf -> fnol (29 fields)
INFO:     127.0.0.1:53890 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:35330 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:20:49,602 | INFO | Created new transport with session ID: 09b854d377eb48ef8dc6cb09ce891e92
INFO:     127.0.0.1:34708 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:34708 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:20:49,610 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:34732 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:20:49,612 | INFO | Terminating session: 09b854d377eb48ef8dc6cb09ce891e92
INFO:     127.0.0.1:34732 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:34722 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:20:52,430 | INFO | Created new transport with session ID: e932773604e742a9b729b16d31ff2316
2026-09-24 09:20:52,433 | INFO | Created new transport with session ID: cbbcef7ed6c7440ba2d33838980a5162
INFO:     127.0.0.1:34742 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:34754 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:34742 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:34754 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:20:52,444 | INFO | Processing request of type CallToolRequest
2026-09-24 09:20:52,445 | INFO | Processing request of type CallToolRequest
2026-09-24 09:20:52,844 | INFO | HTTP Request: GET http://apiserver/claim/CLM-MOT-MUFA5VG0 "HTTP/1.1 200 OK"
INFO:     127.0.0.1:34778 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:20:52,847 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:34778 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:20:52,849 | INFO | Terminating session: e932773604e742a9b729b16d31ff2316
INFO:     127.0.0.1:34778 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:34766 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:21:06,754 | INFO |   [A] b71b9f20-6a43-4fa8-809f-cb9f397acfe2.pdf -> repair_estimate (22 fields)
INFO:     127.0.0.1:49838 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:21:35,564 | INFO |   [A] 7a1e0b3a-0616-4778-a6d4-13558b3bddc6.pdf -> policy_data_coverage (26 fields)
INFO:     127.0.0.1:60622 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:22:03,936 | INFO |   [A] f5f657cd-bd7f-4d39-83d8-7a529948df92.pdf -> driver_statement (17 fields)
INFO:     127.0.0.1:54502 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:22:49,627 | INFO | Created new transport with session ID: 2daac9bf42c84de38c1de825cf5555cf
INFO:     127.0.0.1:45850 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:45850 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:22:49,635 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:45856 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:22:49,637 | INFO | Terminating session: 2daac9bf42c84de38c1de825cf5555cf
INFO:     127.0.0.1:45856 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:45854 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:45838 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:22:51,442 | INFO | Created new transport with session ID: 54ed1333b442410c9bd992fa881fb762
2026-09-24 09:22:51,442 | INFO | Created new transport with session ID: 3be304e154e6456287a2be0edfda5dfe
INFO:     127.0.0.1:45868 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:45884 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:45868 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:45884 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:22:51,455 | INFO | Processing request of type CallToolRequest
2026-09-24 09:22:51,456 | INFO | Processing request of type CallToolRequest
2026-09-24 09:22:51,785 | INFO | HTTP Request: GET http://apiserver/claim/CLM-MOT-MUFAP0ND "HTTP/1.1 200 OK"
INFO:     127.0.0.1:45918 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:22:51,788 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:45918 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:22:51,790 | INFO | Terminating session: 54ed1333b442410c9bd992fa881fb762
INFO:     127.0.0.1:45918 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:45900 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:36368 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:53782 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:33640 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:24:40,954 | INFO |   [A] fe449832-077d-42a4-985b-6bc94f8cde8f.pdf -> repair_estimate (22 fields)
2026-09-24 09:24:49,650 | INFO | Created new transport with session ID: 4e842bfb9f484ca39db4899750dbaeac
INFO:     127.0.0.1:44490 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:44490 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:24:49,661 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:44516 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:24:49,663 | INFO | Terminating session: 4e842bfb9f484ca39db4899750dbaeac
INFO:     127.0.0.1:44516 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:44506 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:44522 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
2026-09-24 09:24:51,772 | INFO | Created new transport with session ID: 8dbb1f0a00cd4c0784c66f31afc47991
2026-09-24 09:24:51,773 | INFO | Created new transport with session ID: 01448f1d07e84738862bf149363ccf04
INFO:     127.0.0.1:44536 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:44542 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:44536 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:44542 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 202 Accepted
2026-09-24 09:24:51,789 | INFO | Processing request of type CallToolRequest
2026-09-24 09:24:51,790 | INFO | Processing request of type CallToolRequest
2026-09-24 09:24:52,129 | INFO | HTTP Request: GET http://apiserver/claim/CLM-MOT-MUFBI8H3 "HTTP/1.1 200 OK"
INFO:     127.0.0.1:44570 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:24:52,132 | INFO | Processing request of type ListToolsRequest
INFO:     127.0.0.1:44570 - "POST /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
2026-09-24 09:24:52,134 | INFO | Terminating session: 8dbb1f0a00cd4c0784c66f31afc47991
INFO:     127.0.0.1:44570 - "DELETE /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:44558 - "GET /api/v1/slm_triage/mcp HTTP/1.1" 200 OK
INFO:     127.0.0.1:58480 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:52584 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
INFO:     127.0.0.1:34690 - "GET /api/v1/intake_validation/poll HTTP/1.1" 200 OK
azureuser@slm-ft-t4:~/Ramakrishna$ tail -50 /tmp/motor_demo_logs/intake.log
2026-09-24 09:16:11,320 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:16:41,619 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:16:41,619 | INFO     | motor_intake_validation_agent | Found 1 claim(s) awaiting intake validation
2026-09-24 09:16:41,619 | INFO     | motor_intake_validation_agent | Processing intake validation for claim=CLM-MOT-MUFBI8H3
2026-09-24 09:16:41,772 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:41,772 | INFO     | mcp.client.streamable_http | Received session ID: 92f9f34785d547888668d24a879e4193
2026-09-24 09:16:41,773 | INFO     | mcp.client.streamable_http | Negotiated protocol version: 2025-11-25
2026-09-24 09:16:41,775 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 202 Accepted"
2026-09-24 09:16:41,777 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:41,779 | INFO     | httpx | HTTP Request: DELETE http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:41,779 | INFO     | motor_intake_validation_agent | Intake validation tools loaded: ['poll_motor_claims_for_validation', 'get_motor_claim_for_validation', 'run_intake_validation']
2026-09-24 09:16:41,821 | WARNING  | motor_intake_validation_agent | Phoenix prompt load failed (Phoenix not configured) — using fallback
2026-09-24 09:16:43,761 | INFO     | httpx2 | HTTP Request: POST https://azureclaimsopenai.openai.azure.com/openai/deployments/gpt-4.1-claims/chat/completions?api-version=2025-01-01-preview "HTTP/1.1 200 OK"
2026-09-24 09:16:43,947 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:43,947 | INFO     | mcp.client.streamable_http | Received session ID: ad88be85819448ff9b287ce46da64e65
2026-09-24 09:16:43,948 | INFO     | mcp.client.streamable_http | Negotiated protocol version: 2025-11-25
2026-09-24 09:16:43,948 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:43,948 | INFO     | mcp.client.streamable_http | Received session ID: 7bb4236103f14c06a2e1a102be4c11e7
2026-09-24 09:16:43,948 | INFO     | mcp.client.streamable_http | Negotiated protocol version: 2025-11-25
2026-09-24 09:16:43,952 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 202 Accepted"
2026-09-24 09:16:43,953 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 202 Accepted"
2026-09-24 09:16:44,274 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:44,276 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:44,278 | INFO     | httpx | HTTP Request: DELETE http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:44,527 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:44,529 | INFO     | httpx | HTTP Request: POST http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:44,531 | INFO     | httpx | HTTP Request: DELETE http://localhost:8500/api/v1/intake_validation/mcp "HTTP/1.1 200 OK"
2026-09-24 09:16:45,785 | INFO     | httpx2 | HTTP Request: POST https://azureclaimsopenai.openai.azure.com/openai/deployments/gpt-4.1-claims/chat/completions?api-version=2025-01-01-preview "HTTP/1.1 200 OK"
INFO:     127.0.0.1:48680 - "POST /process/CLM-MOT-MUFBI8H3 HTTP/1.1" 200 OK
2026-09-24 09:16:46,472 | INFO     | httpx | HTTP Request: POST http://localhost:8501/process/CLM-MOT-MUFBI8H3 "HTTP/1.1 200 OK"
2026-09-24 09:17:16,772 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:17:47,065 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:18:17,322 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:18:47,573 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:19:17,836 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:19:48,127 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:20:18,387 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:20:48,644 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:21:18,906 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:21:49,169 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:22:19,447 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:22:49,710 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:23:19,962 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:23:50,203 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:24:20,537 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:24:50,831 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:25:21,108 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:25:51,403 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:26:21,672 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
2026-09-24 09:26:51,983 | INFO     | httpx | HTTP Request: GET http://localhost:8500/api/v1/intake_validation/poll "HTTP/1.1 200 OK"
azureuser@slm-ft-t4:~/Ramakrishna$ 
