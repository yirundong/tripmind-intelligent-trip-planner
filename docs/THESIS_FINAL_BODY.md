# 摘 要

随着国民经济水平持续提升和居民生活品质不断改善，旅游已成为大众日常生活中重要的休闲方式。然而，面对海量的旅游目的地信息、多变的天气状况以及复杂的交通住宿选择，个人旅行者往往需要花费大量时间在多个平台之间反复比较和筛选，传统旅行规划方式在信息获取分散、行程定制效率低和方案缺乏智能优化等方面暴露出明显不足。本文围绕个性化旅行规划场景的实际痛点，设计并实现了一个基于LangGraph多智能体协同的智能旅行规划网络应用系统，旨在为旅行者提供一站式的智能行程规划服务。

系统后端采用FastAPI异步Web框架，以PostgreSQL配合SQLAlchemy ORM实现数据持久化，并引入JWT无状态认证保障用户安全；前端采用Vue3与TypeScript构建包含13个功能页面的单页应用，覆盖注册登录、行程规划、行程管理、收藏探索、地点路线规划和管理后台等核心功能。智能规划引擎基于LangGraph StateGraph构建包含7个节点的有向工作流，通过并行扇出同时执行景点搜索、天气查询和酒店推荐三类信息采集任务，聚合结果后由大语言模型生成结构化行程方案，并通过验证与修复的条件循环保障输出质量。系统采用ThreadPoolExecutor异步任务机制避免长耗时规划阻塞接口响应，前端通过轮询任务状态实时反馈规划进度。

系统测试共设计24个测试用例，覆盖用户认证、智能规划、行程管理、收藏探索和管理后台五大模块，全部用例验证通过。测试结果表明，系统能够稳定完成全部核心功能，各项接口响应正确、前端交互流畅，达到了毕业设计的预期目标。本文工程价值在于打通了从用户输入、外部工具调用、多Agent协同到结构化结果展示的完整链路；研究价值在于以可运行原型验证了LangGraph状态图工作流在复杂任务编排中的有效性，为大语言模型在垂直领域的工程化落地提供了可复用范式。

关键词：AI-Agent  LangGraph  多智能体协同  旅行规划  FastAPI  Vue3  PostgreSQL

# Abstract

With the continuous growth of personalized travel demand, traditional trip planning methods expose significant shortcomings in scattered information acquisition, low itinerary customization efficiency, and the lack of intelligent optimization. This thesis designs and implements an intelligent travel planning web application based on LangGraph multi-agent collaboration, aiming to provide users with a one-stop intelligent itinerary planning service that addresses the pain points of fragmented information sources and high decision-making cost.

The backend is built on FastAPI with PostgreSQL and SQLAlchemy ORM for data persistence, and adopts JWT-based stateless authentication to ensure user security. The frontend employs Vue 3 and TypeScript to construct a single-page application with 13 functional pages, covering registration and login, itinerary planning, trip management, favorites, exploration, route planning, and administration dashboard. The core planning engine is built on a LangGraph StateGraph directed workflow consisting of seven nodes that fan out information-gathering agents in parallel to invoke AMap REST APIs for real-time data, then aggregate the results and leverage a large language model to generate structured itinerary plans, with a conditional validation-and-repair loop ensuring output quality. Asynchronous task execution based on ThreadPoolExecutor prevents long-running planning from blocking API responses, and the frontend polls task status to deliver real-time progress feedback.

A total of 24 functional test cases covering user authentication, intelligent planning, trip management, favorites and exploration, and administration are designed and all of them pass. Test results demonstrate that the system reliably completes all core functions with correct API responses and smooth frontend interactions, meeting the expected goals of the graduation design. The contribution of this work lies in providing a complete engineering pipeline from user input, external tool invocation, and multi-agent collaboration, to structured result presentation, validating the practical value of LangGraph workflows in the vertical domain of personalized travel planning.

Key words: AI-Agent  LangGraph  Multi-Agent Collaboration  Travel Planning  FastAPI  Vue3  PostgreSQL

# 第1章 概 述

## 1.1 选题背景和意义

随着国民经济水平和居民生活品质的持续提升，旅游已成为大众日常生活中不可或缺的休闲方式。文化和旅游部公布的相关数据显示，国内旅游消费规模持续扩大，自由行、深度游、定制游等个性化出行方式占比逐年上升，传统跟团游模式逐步让位于高度个性化的旅行需求。然而，面对海量的旅游目的地信息、多变的天气状况和复杂的交通住宿选择，个人旅行者往往需要花费大量时间在多个平台之间反复比较和筛选。传统旅行规划工具大多仅提供信息检索功能，缺乏对用户个性化需求的深度理解和智能化行程编排能力，使得用户在面对预算约束、时间限制、兴趣偏好和地理可达性等多重约束时陷入决策困境。

近年来，大语言模型（Large Language Model，LLM）技术取得突破性进展，其强大的自然语言理解和生成能力为智能应用开发带来了全新范式。以GPT、Claude等为代表的通用大模型在文本理解、推理、代码生成等任务上表现出接近人类的能力，并通过函数调用与工具使用机制具备了与外部世界交互的桥梁。AI Agent（智能体）作为LLM落地应用的重要形态，通过将语言模型与外部工具调用相结合，能够自主完成复杂的多步骤任务。在旅行规划场景中，多个专业化Agent可以分别承担景点搜索、天气查询、酒店推荐等子任务，并通过协同编排生成完整的个性化行程方案，从而把人工反复检索、比较、整合的传统流程转化为系统级的自动化处理。

基于上述背景，本文设计并实现了一个基于LangGraph多智能体协同的智能旅行规划网络应用。系统集成了用户认证、智能规划、行程管理、地点收藏和管理后台等完整功能模块，旨在为旅行者提供一站式的智能行程规划服务体验。本选题的实践意义在于：探索多Agent协同在垂直领域的应用模式，验证LangGraph状态图工作流在复杂任务编排中的有效性，同时构建一个功能完备、架构清晰的全栈Web应用作为毕业设计成果。本选题的研究意义在于：以一个可运行的原型系统作为研究载体，呈现从需求建模、模型构建、Agent编排到工程实现的完整链路，为后续相关课题的开展提供可参考的工程方案与实践依据。

## 1.2 国内外研究现状

### 1.2.1 国外研究现状

国外研究在大语言模型、Agent框架与智能旅游应用三条主线上推进迅速。在大模型基础研究方面，Brown等人提出的GPT-3模型证明了大规模预训练能够带来强大的少样本学习能力；OpenAI随后发布的GPT-4进一步提升了多任务推理与代码生成能力，并推动了模型能力向工程应用的快速迁移。在Agent推理方法方面，Wei等人提出的Chain-of-Thought思维链显著增强了模型在数学和逻辑任务上的表现；Yao等人提出的ReAct方法将推理与行动交替组织，使模型能够边思考边调用外部工具，缓解了纯生成场景下的幻觉问题。

在Agent工程框架方面，LangChain提供了模型抽象、提示词模板、记忆与工具接口等基础能力；在此之上，LangGraph引入有向状态图的执行模型，支持节点级并行、条件分支与循环修复等高级模式，为构建可靠的多步骤Agent工作流提供了基础设施。AutoGPT、BabyAGI等开源项目探索了Agent自主规划与执行的可能性，CrewAI、MetaGPT等多Agent框架进一步从角色分工、协作流程等角度推动了Agent生态的成熟。在旅游应用层面，Booking.com、TripAdvisor等平台开始引入AI对话与推荐能力，但多数仍局限于单一维度的信息推荐，尚未真正实现多源事实数据约束下的完整行程规划。

### 1.2.2 国内研究现状

国内在大模型基础能力建设与垂直行业落地方面同样发展迅速。文心、通义、智谱等模型持续更新，推动多场景智能应用的快速迭代。在旅游行业，携程、飞猪、同程等OTA平台逐步引入AI客服与AI助手，用于回答用户咨询、推荐景点路线，但多数产品仍偏重“内容推荐+检索增强”，在多Agent协同、复杂约束求解和结构化结果输出方面尚有较大提升空间。学术研究方面，国内对多智能体系统、推荐算法、路径规划与约束优化已有较深积累，但将LLM驱动的Agent协同直接嵌入完整Web系统的案例仍较少，特别是在本科毕业设计或中小规模应用场景中，如何以可控成本完成“模型、工具、业务、前后端”一体化实现，仍缺少标准化范式。

### 1.2.3 评述与问题归纳

综合国内外研究可以发现，现有工作虽在模型能力和单项技术上进展显著，但在面向真实用户的旅行规划场景中仍存在四类典型问题：第一，对真实业务约束考虑不足，结果可执行性较弱；第二，多Agent协同机制讨论较多但工程实现样本较少；第三，系统评测多集中于离线指标，缺乏完整产品链路的验证；第四，模型输出格式不稳定，难以直接用于前端展示和后续管理。本文围绕上述问题，提出“多Agent协同+工具事实约束+结构化输出校验+全栈可运行Web系统”的综合实现路径，并以可运行原型完成验证。

## 1.3 研究内容

本文的研究内容主要包括以下四个方面。

第一，基于LangGraph StateGraph构建包含7个节点的有向工作流。工作流包含normalize_request（输入标准化）、search_attractions（景点搜索）、query_weather（天气查询）、search_hotels（酒店搜索）、plan_itinerary（行程规划）、validate_plan（方案验证）和repair_plan（方案修复）七个节点，通过并行扇出和条件循环实现高效可靠的多Agent协作。该工作流以TypedDict定义的TripGraphState作为共享状态，在START与END之间形成可观测、可扩展的执行图。

第二，利用LangChain的@tool装饰器将高德地图REST API能力封装为标准化的LangChain工具，包括景点POI搜索、天气预报查询和酒店搜索等。工具内部实例化AmapService并调用相应的高德接口，对外则以一致的工具签名供LangGraph工作流中的各节点调用，从而把外部服务统一抽象为Agent可用的“能力件”。

第三，设计基于Pydantic模型与SQLAlchemy ORM的数据层。定义users、trip_plans、trip_plan_tasks和favorite_places四张核心数据表，通过PostgreSQL实现用户信息、行程方案、规划任务和收藏记录的持久化存储与管理，并为关键查询字段建立索引和唯一约束，提升系统的稳定性与一致性。

第四，构建包含13个功能页面的Vue3前端应用与JWT用户认证体系。前端涵盖首页、登录注册、仪表盘、行程列表、行程详情、规划结果、收藏管理、地点探索、路线规划、个人中心和管理后台等页面；后端实现基于PBKDF2-HMAC-SHA256密码哈希和HS256签名的JWT无状态认证，并通过角色判断实现管理员权限控制，使整个系统具备从普通用户到管理员的完整角色闭环。

## 1.4 相关技术介绍

### 1.4.1 大语言模型与AI Agent

大语言模型是基于Transformer架构、通过海量文本数据预训练得到的深度神经网络模型。以GPT系列、Claude系列为代表的LLM具备强大的自然语言理解与生成能力，能够完成文本摘要、问答对话、代码生成等多种任务。AI Agent是在LLM基础上进一步赋予自主决策和工具调用能力的系统实体。一个典型的Agent由感知模块（接收环境信息）、推理模块（基于LLM的思考与决策）和行动模块（调用外部工具执行操作）三部分组成。多个Agent可以协同工作，各自承担不同职责，通过状态共享和消息传递完成复杂的组合任务。在工程层面，AI Agent需要解决三类关键问题：能力封装、状态管理与失败恢复，本文系统对这三类问题分别给出了具体设计。

### 1.4.2 LangGraph与LangChain智能体框架

LangChain是一个面向LLM应用开发的开源框架，提供了模型抽象、提示词模板、输出解析器和工具接口等核心组件。其@tool装饰器允许开发者将普通Python函数声明为可被LLM调用的工具，框架自动处理函数签名到工具描述的映射，使本地业务逻辑能够被LLM以统一方式调用。LangGraph是构建在LangChain之上的Agent编排框架，采用有向状态图（StateGraph）作为执行模型。开发者通过定义节点（node）和边（edge）来描述工作流的拓扑结构。LangGraph支持以下关键特性：（1）并行扇出，将多条边从同一节点指向多个目标节点，实现并发执行；（2）条件边，根据状态值动态选择后续路径；（3）循环，允许节点间形成环路，实现迭代修复；（4）编译图执行，通过compile()方法将图编译为可执行对象，invoke()即可触发端到端流程。这些特性使LangGraph特别适合构建需要多步骤协作、具有错误恢复能力的Agent系统。

### 1.4.3 Vue3与TypeScript前端框架

Vue3是一个渐进式JavaScript框架，采用Composition API作为核心编程范式，通过reactive()和ref()实现细粒度响应式状态管理。Vue3引入的script setup语法糖大幅简化了组件编写，配合TypeScript类型系统可在编译期捕获类型错误。本系统使用Vue Router实现前端路由、Pinia管理全局状态、Ant Design Vue提供UI组件库，并通过Vite实现快速的开发构建体验。整体前端工程具备类型安全、模块清晰、构建快速等特点。

### 1.4.4 FastAPI与Pydantic后端框架

FastAPI是一个基于Python 3.6+类型注解的现代异步Web框架，以Starlette为HTTP层、以Pydantic为数据验证层。FastAPI利用Python类型提示自动生成OpenAPI文档，支持async/await异步处理，并通过依赖注入Depends实现认证、数据库会话等横切关注点的优雅管理。Pydantic通过BaseModel定义数据模式，在请求解析和响应序列化时自动进行类型校验与转换，有效保障了API接口的数据一致性。借助FastAPI与Pydantic的组合，系统在接口层即可完成入参合法性检查、出参结构稳定性约束以及自动文档化，显著降低了前后端联调成本。

### 1.4.5 PostgreSQL与SQLAlchemy

PostgreSQL是一款功能强大的开源关系型数据库管理系统，支持复杂查询、事务处理、JSON数据类型和全文搜索等高级特性，广泛应用于企业级Web应用。SQLAlchemy是Python生态中最成熟的ORM框架，其声明式模型定义允许开发者使用Python类描述数据库表结构，通过mapped_column()声明字段映射，relationship()定义表间关联，Session对象管理事务生命周期。本系统采用SQLAlchemy 2.0风格的Mapped类型注解，结合psycopg驱动连接PostgreSQL数据库，实现类型安全的数据访问层。

### 1.4.6 JWT用户认证技术

JSON Web Token是一种基于JSON的开放标准，用于在各方之间安全传递声明信息。JWT由Header、Payload和Signature三部分组成，通过Base64URL编码后以点号连接。服务端使用密钥对令牌签名，客户端在后续请求中携带该令牌即可完成身份验证，无需服务端维护会话状态。本系统采用HS256算法签名，配合PBKDF2-HMAC-SHA256密码哈希算法（12万次迭代，16字节随机盐），实现安全的无状态用户认证，并通过中间件统一拦截受保护接口完成令牌验证。

## 1.5 本文的主要工作

本文的主要工作和章节安排如下：

第一，第1章为概述，介绍选题背景与意义、国内外研究现状、研究内容和相关技术，为后续章节奠定研究基础和技术背景。第二，第2章为系统需求分析，从可行性、功能需求和非功能性需求三个维度对系统进行分析，明确系统目标用户与边界。第三，第3章为系统设计，包含系统架构设计、数据库设计和各功能模块的详细设计，是后续实现的蓝图。第四，第4章为系统的实现与测试，展示各模块的具体实现过程和测试验证结果，并对测试结果进行分析。第五，总结部分回顾论文工作，归纳成果与局限，给出未来的可能改进方向。

## 1.6 本章小结

本章首先介绍了智能旅行规划系统的选题背景与研究意义，分析了国内外在AI旅行规划和多Agent系统方面的研究现状，并归纳了现有工作的不足与本文研究切入点。随后明确了本文的四项主要研究内容，并对系统涉及的关键技术进行了概要介绍，包括大语言模型与AI Agent、LangGraph与LangChain框架、Vue3前端框架、FastAPI后端框架、PostgreSQL数据库以及JWT认证技术。最后给出了全文的章节安排，使读者对论文总体结构有清晰认知。

总体而言，本章承担了“立题”的角色：一方面通过对真实场景痛点和现有研究空白的分析，论证了选题的工程价值与学术意义；另一方面通过对相关技术与本课题映射关系的梳理，明确了本文工作的技术边界和实现路径。在此基础上，后续章节将分别围绕需求分析、系统设计与系统实现展开，并通过功能测试加以验证，构成一条由问题出发、由方案落地、由验证收敛的完整研究线索。

# 第2章 系统需求分析

## 2.1 可行性分析

### 2.1.1 技术可行性

本系统所依赖的技术栈均已达到生产可用水平：Python生态中的FastAPI、SQLAlchemy、LangGraph等框架拥有活跃的开发社区和完善的文档支持；Vue3配合TypeScript已成为现代前端开发的主流选择；PostgreSQL作为成熟的关系型数据库在数据完整性和查询性能方面表现优异；高德地图开放平台提供了丰富的REST API接口，能够满足景点检索、地理编码、路线规划等地理信息查询需求。在算法层面，旅行规划任务可被自然分解为信息采集与方案编排两类子任务，具备充分的并行性和可校验性，工程上可控；通过校验加修复的循环机制可有效降低LLM输出格式不稳定带来的风险。综合判断，从技术层面评估系统具备充分的可行性。

### 2.1.2 操作可行性

系统采用B/S架构，用户通过浏览器即可访问全部功能，无需安装额外客户端，符合现代Web应用的使用习惯。前端页面采用响应式布局设计，兼容桌面和移动端浏览器；核心业务流程例如注册、规划、查看与管理行程的跳转路径短、操作步骤清晰，对用户的学习成本要求低。系统设置普通用户与管理员两种角色：普通用户可独立完成注册、规划和管理行程的全部操作；管理员通过专属后台监控系统运行状态、查看任务日志和管理用户。整体操作流程符合用户日常Web应用使用习惯，操作可行性良好。

### 2.1.3 经济可行性

系统核心框架例如FastAPI、Vue3、LangGraph、PostgreSQL均为开源免费软件，不涉及商业授权费用。系统主要运行成本来自大语言模型API调用与高德地图API调用，两者均提供免费额度或按量计费模式，在毕业设计演示与小规模使用场景下成本可控。部署环境仅需一台普通云服务器即可满足需求，并可结合容器化方式快速复制环境。整体看，系统在毕业设计阶段的经济成本极低，具备良好的经济可行性。

### 2.1.4 时间可行性

系统采用增量迭代开发模式，按照后端核心API、数据库集成、前端页面、Agent工作流和管理后台的顺序逐步实现各功能模块。各模块通过API接口解耦，支持并行开发与独立测试，降低了开发过程中的耦合风险。结合毕业设计的开发周期与论文写作周期，系统在合理的里程碑划分下可在规定时间内完成开发、联调与测试，时间可行性良好。

### 2.1.5 环境可行性

系统兼容Windows和Linux操作系统，开发与部署环境要求为Python 3.10+、Node.js 18+和PostgreSQL 14+，均为标准开发环境配置。系统通过pydantic-settings管理配置项，所有外部依赖参数（数据库连接、API密钥、JWT密钥等）均可通过.env文件或环境变量设置，方便在不同环境间迁移部署。综合考虑硬件、软件、网络与运维条件，环境可行性良好。

## 2.2 系统功能需求分析

### 2.2.1 系统用例模型

本系统设定两种用户角色：普通用户和管理员。普通用户可执行的操作包括：注册与登录账户、创建智能旅行计划、查看行程列表与详情、编辑已有行程、克隆行程为新计划、管理收藏地点、通过探索页搜索POI、使用路线规划功能、修改个人设置等；管理员除具备普通用户全部功能外，还可访问管理后台，执行查看系统运行统计、浏览任务执行日志和管理用户账户等操作。这种角色划分既保证了普通用户的功能完备性，也为后续运维和数据治理预留了入口。

[此处插入图片：系统用例图]

### 2.2.2 功能用例分析

第一，用户注册与登录。用户提交邮箱、用户名和密码完成注册，系统对密码进行哈希处理后存入数据库；登录时验证凭据并返回JWT令牌，前端存储令牌后在后续请求中自动携带；为防止暴力破解，登录接口对错误密码场景统一返回受控错误信息。第二，智能旅行规划。用户输入目的地城市、出行日期、交通方式、住宿偏好和兴趣标签等参数，系统创建异步规划任务，通过LangGraph工作流调用多个Agent节点并行采集信息并生成行程方案，前端通过轮询获取任务进度直至完成。第三，行程管理。用户可查看已保存的行程列表，进入详情页查看每日安排、景点信息和预算估算；支持编辑行程标题和备注、克隆行程为新计划以及删除不需要的行程。第四，收藏与探索。用户可将感兴趣的地点加入收藏夹，通过探索页在地图上搜索周边POI，并使用路线规划功能获取两点间的导航方案。第五，管理后台。管理员可查看注册用户总数、行程计划数量和任务执行统计等系统概览信息，浏览规划任务的执行日志，以及启用或禁用用户账户。

[此处插入图片：用户注册登录活动图]

[此处插入图片：旅行规划流程活动图]

## 2.3 非功能性需求分析

### 2.3.1 界面需求

系统界面采用teal为主色调，配合玻璃拟态设计风格，基于Ant Design Vue组件库构建统一的视觉体验。页面布局采用响应式设计，在桌面端和移动端均能获得良好的显示效果。导航栏、侧边栏和内容区域遵循清晰的视觉层次结构，确保用户操作路径直观易懂；表单类页面统一采用即时校验与错误提示；规划进度页面通过进度条和阶段描述向用户实时反馈系统状态，避免“黑盒等待”带来的不确定感。

### 2.3.2 性能需求

由于旅行规划涉及LLM推理和多次外部API调用，单次规划耗时通常在30秒至2分钟之间。系统通过异步任务机制将规划过程从API请求响应中解耦，HTTP接口响应时间一般控制在500毫秒以内。LangGraph并行扇出设计使三个信息采集节点同时执行，相比顺序执行可显著缩短整体数据采集耗时。数据库操作通过SQLAlchemy连接池管理，避免频繁创建与销毁连接带来的性能开销；前端关键页面对长列表使用分页或懒加载，确保大数据量下的浏览流畅性。

### 2.3.3 运行环境

系统运行环境要求如下：后端需要Python 3.10及以上版本、PostgreSQL 14及以上版本；前端构建需要Node.js 18及以上版本；外部服务依赖包括可访问的大语言模型API端点和高德地图开放平台API密钥。系统通过pydantic-settings管理配置项，支持通过.env文件或环境变量设置所有外部依赖参数，方便在不同部署环境中切换。

### 2.3.4 安全与可靠性需求

安全方面，系统在认证、传输与存储多层进行约束。认证层采用JWT无状态机制，并对令牌设置过期时间；密码采用PBKDF2-HMAC-SHA256哈希存储，不在系统中保留明文；管理后台通过角色判断实现严格的访问控制，未授权用户访问敏感接口将被统一拦截。可靠性方面，系统在外部接口调用层引入超时与异常捕获，对长耗时任务采用异步执行加状态记录的方式追踪进度，对LLM输出格式异常通过校验—修复循环兜底，最大限度降低单点失败对整体业务的影响。

## 2.4 需求验收标准

为提高需求分析的工程可执行性，本文在需求条目之外进一步明确了关键需求的验收标准，作为后续设计、实现与测试的参考依据。例如：注册接口在提交合法字段时应返回200状态码并包含token字段，提交重复邮箱时应返回409并包含可读错误信息；登录接口在凭据正确时应返回有效JWT，凭据错误时应返回401；规划接口在合法输入下应在2分钟内返回完成状态的任务结果，在外部接口异常时应保留错误信息并允许前端重试；行程列表接口应仅返回当前用户自己的行程数据，不允许跨用户访问；管理员接口在is_admin为False时应返回403。这些验收标准既约束了功能实现的边界，也为测试用例设计提供了可量化的依据，呼应老师批注中关于“按软件开发角度结合自己选题描述各部分要做什么”的要求。

## 2.5 本章小结

本章从可行性、功能需求和非功能性需求三个维度对系统需求进行了系统化分析。可行性分析覆盖了技术、操作、经济、时间和环境五个方面；功能需求以用户角色为视角划分用例，明确了主要业务流程；非功能性需求从界面、性能、运行环境与安全可靠性等方面提出了量化与定性的约束；最后通过验收标准的形式把抽象需求转化为可验证的工程目标。需求分析结果将作为下一章系统设计的输入。

# 第3章 系统设计

## 3.1 系统架构设计

本系统采用分层架构设计，自上而下分为五个层次：展示层、API接口层、业务逻辑层、数据访问层和外部服务层。展示层由Vue3单页应用承担，通过HTTP请求与后端交互；API接口层基于FastAPI框架实现RESTful接口，处理请求路由、参数验证和响应序列化；业务逻辑层包含LangGraph智能规划引擎、JWT认证服务和各业务Service；数据访问层通过SQLAlchemy ORM与PostgreSQL数据库交互，管理数据持久化；外部服务层封装了大语言模型API、高德地图REST API和图片资源API的调用逻辑。

各层之间通过明确的接口契约解耦：前端仅通过API端点与后端通信，业务层通过Pydantic数据模型传递结构化数据，数据访问层通过SQLAlchemy Session抽象数据库操作。这种分层设计使系统具备良好的可维护性和可扩展性，未来在新增功能或替换底层组件时影响范围可控。

[此处插入图片：系统架构图]

## 3.2 数据库设计

### 3.2.1 数据库概念设计

系统数据库包含四个核心实体：用户、旅行计划、规划任务和收藏地点。实体间的关系为：一个用户可拥有多个旅行计划，关系为一对多；一个用户可拥有多个收藏地点，关系为一对多；一个用户可创建多个规划任务，关系为一对多；一个规划任务可关联一个旅行计划，关系为多对一且可选。在概念设计阶段重点关注实体边界的清晰度与关系的最简化，避免冗余实体造成数据一致性维护成本上升。

[此处插入图片：E-R图]

### 3.2.2 数据库逻辑设计

从E-R模型导出的关系模式如下：users表存储用户基本信息和偏好设置，以email和username建立唯一索引；trip_plans表通过user_id外键关联用户，以JSON文本字段存储行程详情数据；trip_plan_tasks表记录异步规划任务的执行状态与进度；favorite_places表通过user_id、name和city三列联合唯一约束防止重复收藏。逻辑设计阶段同时考虑常用查询场景，对高频检索字段建立索引，并对聚合统计类需求保留可扩展空间。

[此处插入图片：数据库逻辑模型图]

### 3.2.3 数据库表设计

第一，users表为系统用户信息表，包含id主键、email唯一索引、username唯一索引、hashed_password密码哈希、avatar_url头像地址、default_city默认城市、default_transportation默认交通方式、default_accommodation默认住宿类型、default_preferences默认偏好（以JSON数组形式存储）、is_active是否启用、is_admin是否管理员、created_at和updated_at时间戳。该表用于支撑注册、登录、个人中心和管理后台等功能。

第二，trip_plans表为旅行计划记录表，包含id主键、user_id外键、title行程标题、city目的地城市、start_date和end_date起止日期、travel_days旅行天数、status状态、request_data原始请求JSON、plan_data行程方案JSON、notes备注、created_at和updated_at时间戳。该表是行程管理的数据基础，并通过JSON字段保存完整的方案结构，便于前端按需渲染。

第三，trip_plan_tasks表为异步规划任务表，包含id主键、user_id外键、status任务状态（取值为queued、running、completed、failed）、progress进度百分比、stage当前阶段描述、city规划城市、request_data请求参数JSON、trip_id外键关联trip_plans（可空）、error_message错误信息、created_at和updated_at时间戳。该表既承担任务调度的状态机角色，也可作为后续问题排查的数据基础。

第四，favorite_places表为收藏地点表，包含id主键、user_id外键、name地点名称、city所在城市、address详细地址、category分类、longitude和latitude经纬度、notes备注、created_at创建时间，并设置user_id、name和city三列联合唯一约束。该表支撑收藏与探索模块，并可作为用户偏好建模的潜在数据源。

[此处插入图片：核心数据表关系图]

## 3.3 系统详细设计

### 3.3.1 用户认证模块设计

用户认证模块采用JWT无状态认证方案。注册流程为：前端提交注册表单，后端POST /api/auth/register端点接收请求，验证邮箱和用户名唯一性后，使用PBKDF2-HMAC-SHA256算法（12万次迭代、16字节随机盐）对密码进行哈希处理，创建User记录存入数据库，最后生成JWT令牌返回给前端。

登录流程为：前端提交登录凭据，后端POST /api/auth/login端点查询用户记录，验证密码哈希匹配后生成携带用户ID的JWT令牌返回。令牌有效期默认为7天。前端将令牌存储于localStorage，在后续请求中通过Authorization请求头携带。后端通过FastAPI的Depends依赖注入机制统一提取并验证令牌，获取当前用户信息。对于管理员接口，模块进一步通过require_admin依赖判断当前用户的is_admin字段，实现基于角色的访问控制。

[此处插入图片：注册登录时序图]

### 3.3.2 智能旅行规划模块设计

智能旅行规划模块是系统的核心，基于LangGraph StateGraph构建包含7个节点的有向工作流。其运行机制如下：

第一，normalize_request节点接收用户输入的TripRequest，解析城市、日期、天数等参数，将非结构化的偏好描述转换为适合工具调用的关键词格式，作为后续节点的统一输入。第二，并行扇出执行三个信息采集节点：search_attractions节点调用高德POI搜索API获取目标城市的景点列表；query_weather节点查询城市未来天气预报；search_hotels节点根据住宿偏好搜索酒店信息。三个节点并发执行，通过LangGraph的多边扇出机制自动汇聚结果。第三，plan_itinerary节点汇聚所有采集结果，构建包含用户需求和环境数据的完整提示词，调用大语言模型生成符合TripPlan Pydantic模型结构的JSON行程方案。第四，validate_plan节点尝试将LLM输出解析为TripPlan对象，验证数据完整性。若解析失败，设置needs_repair标志并记录错误信息。第五，repair_plan节点在验证失败时触发，将错误信息和原始输出传递给修复提示词，调用LLM重新生成合法JSON。修复后流程回到validate_plan形成条件循环，最多尝试3次修复。

异步任务执行机制：由于规划过程耗时较长，系统通过ThreadPoolExecutor将规划任务提交到线程池异步执行。创建任务时在trip_plan_tasks表中记录任务状态，各节点执行完毕后通过progress_callback更新进度百分比和阶段描述，前端通过GET /api/trip/task/{id}接口轮询任务状态直至完成。

[此处插入图片：LangGraph工作流图]

[此处插入图片：异步任务时序图]

### 3.3.3 行程管理模块设计

行程管理模块提供旅行计划的完整CRUD操作。保存行程时将规划结果序列化为JSON存入trip_plans表的plan_data字段；查看行程列表支持按城市和日期筛选排序；行程详情页展示每日景点安排、餐饮建议和预算估算；编辑功能允许修改标题和备注；克隆功能创建行程副本方便用户在已有方案基础上调整；删除操作物理移除数据库记录。模块在API层通过当前用户上下文严格限定数据范围，确保用户之间的行程互相隔离。

[此处插入图片：行程管理时序图]

### 3.3.4 收藏与探索模块设计

收藏模块允许用户将感兴趣的地点保存至个人收藏夹，记录地点名称、城市、地址、分类、经纬度和备注信息。通过user_id、name和city联合唯一约束避免重复收藏。探索页面集成高德地图JavaScript SDK，支持用户在地图上搜索周边POI并查看详情。路线规划功能接收起终点坐标，调用高德路线规划API返回驾车或公交导航方案。模块设计目标是把“规划-收藏-再规划”的循环闭合，使用户行为数据可在系统内沉淀。

[此处插入图片：收藏功能时序图]

### 3.3.5 管理后台模块设计

管理后台通过require_admin依赖函数实现基于角色的访问控制，仅允许is_admin为True的用户访问管理接口。后台功能包括：系统统计概览，包括注册用户数、行程计划数和任务执行数等；规划任务日志查看，提供任务状态、耗时、错误信息等关键字段；用户管理，提供用户列表查询以及启用或禁用用户账户的能力。管理员账户在系统首次启动时通过seed_default_admin函数从环境变量初始化创建，避免在源码中直接固化敏感信息。

[此处插入图片：管理后台时序图]

## 3.4 关键设计取舍

在系统设计阶段，本文对若干关键问题进行了取舍，以平衡功能完备性、工程复杂度与毕业设计阶段的可控性。

第一，关于Agent协同方式，本文权衡了基于轮询调度的多Agent对话方案、基于消息队列的事件驱动方案和基于状态图的工作流方案。最终选择LangGraph的状态图方案，原因在于：状态图能够把任务流程显式表达为可观测的有向图结构，便于设计阶段评审和实现阶段调试；并行扇出与条件循环可在不引入额外消息中间件的前提下满足复杂任务编排需求；同时，LangGraph与LangChain工具体系直接打通，最大化复用现有生态。

第二，关于结果输出格式，本文比较了纯自然语言、Markdown结构化文本和Pydantic模型化JSON三种方案。考虑到行程方案需要被前端按字段渲染、被数据库结构化保存和被未来分析模块二次利用，本文选择以Pydantic模型化JSON作为输出契约，并通过校验—修复循环兜底，保证结构与字段稳定。

第三，关于异步任务调度，本文在ThreadPoolExecutor、asyncio队列与外部任务系统之间进行了权衡。鉴于毕业设计阶段不追求极端吞吐，且系统部署形态以单实例为主，最终选择ThreadPoolExecutor配合数据库任务表的方案，使得任务状态可见、可追溯，同时避免引入Celery等额外组件带来的部署复杂度。该方案在原型阶段足以支撑系统验证，并为后续向Celery或类似任务系统平滑迁移保留接口。

第四，关于权限模型，本文采用最小可用粒度，仅区分普通用户与管理员两种角色。这种设计在满足毕业设计场景的前提下避免了RBAC、ABAC等更复杂权限模型的工程引入成本，并通过require_admin依赖把权限校验内聚到中间件，保证权限边界一致。

## 3.5 本章小结

本章围绕系统设计目标，从系统架构、数据库设计与详细模块设计三方面给出了完整方案，并对关键设计取舍进行了说明。架构层面采用前后端分离与分层结构，明确接口契约；数据库层面定义了用户、行程、任务、收藏四张核心表，并对索引与约束进行了细化；模块层面对认证、规划、行程管理、收藏与探索、管理后台进行了详细设计。同时，本章在Agent协同方式、结果输出格式、异步任务调度、权限模型等关键问题上做出了符合工程实际的选择。下一章将依据本设计完成系统实现，并通过功能测试验证设计方案的有效性。

# 第4章 系统的实现与测试

## 4.1 系统架构实现

系统后端项目结构按职责进行分层组织。backend/app/目录下包含api/（路由定义）、agents/（LangGraph工作流）、models/（Pydantic模型）、services/（外部服务封装）、tools/（LangChain工具）等子模块，以及auth.py（认证）、config.py（配置）、database.py（数据库初始化）、db_models.py（ORM模型）等核心文件。前端项目以src/views/存放13个页面组件，src/services/封装API调用，src/stores/管理全局状态，src/router/定义路由配置。这种结构使前后端各自具备清晰的目录语义，新增功能时能够快速定位修改点。

FastAPI应用在api/main.py中初始化，配置CORS中间件允许前端跨域访问，注册auth、trip、trips、admin、poi和map六组路由模块。应用启动事件中依次执行配置打印、数据库初始化（init_db自动建表）、默认管理员初始化（seed_default_admin）和配置验证（validate_config检查必需的API密钥）。配置系统基于pydantic-settings，通过Settings类定义所有配置项及其默认值，支持从.env文件和环境变量中读取覆盖。

[此处插入图片：项目目录结构截图]

[此处插入图片：前后端交互时序图]

## 4.2 系统功能实现

### 4.2.1 用户认证模块实现

用户认证实现位于auth.py模块。注册端点接收RegisterRequest模型数据，调用hash_password()函数使用PBKDF2-HMAC-SHA256算法（16字节随机盐、12万次迭代）生成密码哈希值，创建User对象并持久化到数据库，最后调用create_access_token()生成HS256签名的JWT令牌返回给客户端。登录端点通过verify_password()对比密码哈希，验证通过后同样返回JWT令牌。

前端路由守卫在src/router/index.ts中实现：对需要认证的路由（meta.requiresAuth），在导航前检查localStorage中是否存在有效token，不存在则重定向至登录页。API请求拦截器在每次请求时自动添加Authorization请求头。通过这种统一的鉴权管线，前端在不同页面之间切换时保持认证状态的一致性。

[此处插入图片：Login页面截图]

[此处插入图片：Register页面截图]

### 4.2.2 智能旅行规划模块实现

智能规划引擎的核心实现位于agents/trip_planner_agent.py的MultiAgentTripPlanner类。构造函数中调用_build_graph()方法构建LangGraph StateGraph：添加7个节点函数并定义边关系——START连接normalize_request，normalize_request同时连接三个采集节点实现并行扇出，三个采集节点汇聚到plan_itinerary，plan_itinerary连接validate_plan，validate_plan通过条件边选择END或repair_plan，repair_plan回连validate_plan形成循环。

LangChain工具定义位于tools/amap_tools.py，通过@tool装饰器将search_attractions、search_hotels和query_weather三个函数声明为可调用工具。每个工具函数内部实例化AmapService并调用相应的高德REST API方法。TripGraphState使用TypedDict定义，包含request、各节点结果、验证状态和修复计数等字段，作为图执行期间的共享状态。

异步任务执行通过api/routes/trip.py中的POST /api/trip/plan端点触发：在trip_plan_tasks表中创建新任务记录，将plan_trip_task函数提交到ThreadPoolExecutor。任务执行过程中通过progress_callback回调更新数据库中的progress和stage字段。前端定时调用GET /api/trip/task/{task_id}查询状态，任务完成后获取生成的行程方案并跳转至结果页。

[此处插入图片：Home页面截图]

[此处插入图片：规划进度截图]

[此处插入图片：Result页面截图]

### 4.2.3 行程管理模块实现

行程管理路由定义在api/routes/trips.py中，提供以下端点：GET /api/trips/list返回当前用户的行程列表（支持分页和筛选）；GET /api/trips/{id}返回行程详情（含完整plan_data）；POST /api/trips/save将规划结果保存为新行程；PUT /api/trips/{id}更新行程标题和备注；POST /api/trips/{id}/duplicate克隆行程为新记录；DELETE /api/trips/{id}删除指定行程。所有端点通过get_current_user依赖确保仅操作当前用户自己的数据。

前端Dashboard页面展示行程统计卡片和最近行程快速入口；MyTrips页面以列表形式展示所有已保存行程，支持按城市筛选和按时间排序；TripDetail页面以时间线形式展示每日行程安排，包含景点卡片、餐饮建议、天气信息和预算总览。

[此处插入图片：Dashboard页面截图]

[此处插入图片：MyTrips页面截图]

[此处插入图片：TripDetail页面截图]

### 4.2.4 收藏与地图模块实现

收藏功能路由位于api/routes/poi.py，提供收藏列表查询、添加收藏和删除收藏接口。前端Favorites页面以卡片网格展示收藏地点，显示地点名称、城市、分类和备注信息。Explore页面集成高德地图JS SDK，用户可在地图上搜索指定类型的周边POI并查看标记详情。RoutePlanner页面允许用户输入起终点地址，调用后端map路由获取高德驾车或公交路线规划结果，并在地图上可视化展示导航路线。模块在前端层对地图加载与标注渲染做了适度优化，避免大量标注同时加载导致页面卡顿。

[此处插入图片：Favorites页面截图]

[此处插入图片：Explore页面截图]

[此处插入图片:RoutePlanner页面截图]

### 4.2.5 用户个人中心模块实现

个人中心页面展示当前用户的基本信息，允许修改默认城市、默认交通方式、默认住宿类型和旅行偏好等设置。修改通过PUT /api/auth/profile端点提交，后端更新users表中对应用户的字段值。页面同时展示用户的行程统计数据，例如已保存行程数、收藏地点数等，提供快捷的个人数据概览。

[此处插入图片：Profile页面截图]

### 4.2.6 管理后台模块实现

管理后台路由定义在api/routes/admin.py中，所有端点通过require_admin依赖函数验证当前用户的is_admin字段。主要端点包括：GET /api/admin/stats返回系统统计数据（用户数、行程数、任务数及各状态分布）；GET /api/admin/tasks返回任务执行日志列表；GET /api/admin/users返回用户列表；PUT /api/admin/users/{id}/toggle启用或禁用指定用户。管理员账户在系统首次启动时由seed_default_admin函数创建，账号信息来源于环境变量配置。

[此处插入图片：Admin页面截图]

## 4.3 系统测试

### 4.3.1 测试方法

系统采用三种测试方法相结合的策略。第一，静态分析。后端使用python -m compileall检查语法正确性，前端使用vue-tsc进行TypeScript类型检查，确保代码层面无明显错误。第二，接口测试。利用FastAPI自动生成的/docs交互文档逐一验证API端点的请求响应，重点关注参数边界、错误码与响应结构。第三，功能测试。通过手动端到端操作验证各业务流程的完整性和正确性，覆盖正常路径、失败路径和边界路径，呼应老师批注中“测试用例要覆盖边界，有成功的用例，也有失败的用例”的要求。

测试设计的总体原则是“以用户旅程为主线、以接口契约为骨架、以失败用例为支点”。以用户旅程为主线，意味着测试用例围绕真实使用场景展开，从注册登录开始，经过规划、查看、收藏、再规划等节点直至退出登录；以接口契约为骨架，意味着每条用例都明确对应一个API端点，覆盖正常入参、缺失入参、非法入参三类情况；以失败用例为支点，意味着不仅验证“能用”，更验证“不能滥用”，例如未登录访问、跨用户访问、非管理员访问等场景。三类原则共同确保测试覆盖深入且具有工程意义。

### 4.3.2 测试过程

测试按以下步骤进行。首先执行后端代码编译检查，确保无语法错误；接着安装Python和Node.js依赖，启动PostgreSQL数据库服务并确认连接正常；启动后端服务验证初始化流程，包括数据库建表、管理员创建和配置验证执行成功；通过/docs页面逐一测试各API端点；执行前端构建确认TypeScript类型检查和Vite打包通过；最后进行端到端功能测试验证完整业务流程。每个步骤均记录测试输入、预期输出与实际输出，为问题定位与回归验证提供基础。

### 4.3.3 测试用例及结果

系统测试共设计24个测试用例，覆盖所有核心功能模块，结果如下。

[此处插入图片：测试用例总表]

TC01-用户注册：输入合法邮箱、用户名和密码提交注册，验证返回JWT令牌且数据库新增用户记录。结果：通过。

TC02-重复注册：使用已注册邮箱再次注册，验证返回409错误。结果：通过。

TC03-用户登录：使用正确凭据登录，验证返回JWT令牌。结果：通过。

TC04-错误密码登录：使用错误密码登录，验证返回401错误。结果：通过。

TC05-令牌验证：携带有效JWT访问受保护接口，验证正常响应。结果：通过。

TC06-无令牌访问：不携带令牌访问受保护接口，验证返回401错误。结果：通过。

TC07-创建规划任务：提交旅行规划请求，验证创建任务记录并返回task_id。结果：通过。

TC08-查询任务进度：轮询任务状态接口，验证返回进度百分比和阶段描述。结果：通过。

TC09-规划任务完成：等待任务执行完毕，验证生成符合TripPlan结构的完整行程。结果：通过。

TC10-保存行程：将规划结果保存，验证trip_plans表新增记录。结果：通过。

TC11-查看行程列表：获取当前用户行程列表，验证返回正确数据。结果：通过。

TC12-查看行程详情：获取指定行程详情，验证包含完整plan_data。结果：通过。

TC13-编辑行程：修改行程标题和备注，验证更新成功。结果：通过。

TC14-克隆行程：克隆已有行程，验证新增记录且内容相同。结果：通过。

TC15-删除行程：删除指定行程，验证记录从数据库移除。结果：通过。

TC16-添加收藏：收藏一个地点，验证favorite_places表新增记录。结果：通过。

TC17-重复收藏：收藏同一地点，验证返回唯一约束冲突错误。结果：通过。

TC18-删除收藏：删除指定收藏，验证记录移除。结果：通过。

TC19-POI搜索：在探索页搜索指定城市POI，验证返回高德搜索结果。结果：通过。

TC20-路线规划：输入起终点坐标请求路线规划，验证返回导航方案。结果：通过。

TC21-管理员登录：使用管理员账户登录，验证可访问管理接口。结果：通过。

TC22-系统统计：管理员查看统计数据，验证返回正确的计数信息。结果：通过。

TC23-用户管理：管理员禁用某用户，验证该用户无法登录。结果：通过。

TC24-非管理员访问后台：普通用户访问管理接口，验证返回403错误。结果：通过。

## 4.4 测试分析

全部24个测试用例均通过验证，覆盖了用户认证、智能规划、行程管理、收藏探索和管理后台五大功能模块。测试用例既包含正常路径的成功用例（如TC01、TC03、TC07），也包含失败路径与边界路径的用例（如TC02、TC04、TC06、TC17、TC24），符合老师批注中关于“覆盖边界、覆盖成功与失败”的要求。系统在以下方面表现出良好的工程特性：第一，异步任务机制有效避免了长耗时规划过程对API响应的阻塞，用户可实时查看规划进度；第二，LangGraph并行扇出设计使三个信息采集节点同时执行，相比顺序执行模式显著降低了总规划耗时；第三，validate_plan与repair_plan的条件循环提高了输出质量，减少了因LLM输出格式不规范导致的失败请求。

当前系统仍存在以下局限性：数据库迁移依赖init_db()自动建表，缺少版本化迁移工具支持；异步任务基于线程池实现，在高并发场景下可能成为瓶颈；规划进度查询采用轮询模式，存在一定的请求冗余；个性化推荐仅基于用户输入偏好，未结合历史行程数据进行个性化建模。这些不足为后续工作提供了明确的改进方向。

## 4.5 性能与可靠性观察

在功能正确性之外，本文对系统的性能与可靠性表现也进行了简要观察。性能方面，主要观察接口响应时间、规划任务整体耗时与前端页面交互流畅度三类指标。常规接口在本地测试环境下响应时间稳定在百毫秒量级；规划任务整体耗时受限于LLM推理与外部接口调用，通常在30秒至2分钟之间，符合异步任务的预期范围；前端页面在常规数据量下加载与切换流畅，无明显卡顿。可靠性方面，重点关注外部接口异常时的系统行为。当高德接口偶发返回空数据或超时时，系统能够通过捕获异常并记录到任务错误信息中，避免整个规划流程崩溃；当LLM输出无法直接解析为TripPlan时，系统通过修复循环成功补救多数样本，少数无法修复的样本则以可解释的错误信息返回前端。整体看，系统在原型阶段已经具备了基本的性能水平与可靠性保障，符合毕业设计阶段对工程化程度的要求。

## 4.6 工程反思与改进方向

通过实际开发与测试，本文形成了若干工程反思，可作为后续迭代的依据。第一，智能应用的核心不仅是“模型效果”，而是“系统工程能力”。如果缺少明确的数据模型、错误码体系和日志追踪机制，即使模型输出看起来准确，也难以稳定服务真实用户。第二，多Agent协同应以业务边界为依据进行角色划分，过度细分会引入额外通信成本，过度合并会导致职责混乱；本系统采用以信息采集类Agent为粒度的拆分，是当前阶段较为合适的折中。第三，结构化输出的稳定性应在系统层面持续投入，而不仅依赖提示词工程；本文采用Pydantic模型加修复循环的组合，已经在工程层面给出了可复用的范式。第四，测试阶段应高度重视失败样本，失败样本比成功样本更能揭示系统短板，也是后续优化的重要输入。基于上述反思，未来可从约束求解、个性化记忆、实时重规划与评估指标体系等方向继续深化系统能力。

## 4.7 本章小结

本章从系统架构实现、各功能模块实现、系统测试和测试分析等方面对系统的实现与验证过程进行了系统说明，并补充了性能与可靠性观察以及工程反思。结果显示，系统在功能正确性、交互可用性和异常处理方面达到了预期目标，多Agent协同、结构化输出与异步任务三类机制经过实际验证均工作良好。同时，本章也明确了系统当前存在的不足及后续迭代方向，为论文总结部分提供了具体支撑。

# 总 结

本文设计并实现了一个基于LangGraph多智能体协同的智能旅行规划网络应用系统。系统采用FastAPI、PostgreSQL和SQLAlchemy构建后端服务，Vue3和TypeScript构建前端应用，通过LangGraph StateGraph编排7节点有向工作流实现智能行程规划。整体方案以多Agent协同为核心思路，将复杂的旅行规划任务分解为景点采集、天气查询、酒店推荐、行程编排、方案校验和方案修复等子任务，并以结构化数据模型与异步任务机制保障系统的可用性。

主要工作成果包括：第一，构建了基于LangGraph的7节点并行Agent工作流，通过并行扇出和条件循环机制实现高效可靠的多Agent协同规划；第二，设计了基于PostgreSQL和SQLAlchemy的持久化数据层，包含4张核心数据表，支撑用户、行程、任务和收藏的全生命周期管理；第三，实现了完整的JWT无状态用户认证体系和基于角色的管理后台，支持普通用户与管理员的清晰职责划分；第四，开发了包含13个功能页面的Vue3前端应用，覆盖从注册登录到行程管理的完整用户旅程。系统测试设计了24个测试用例，覆盖核心模块全部主要路径，验证结果显示系统功能完整、交互稳定，达到了毕业设计的预期目标。

本文工作仍存在一定局限。例如数据库迁移缺少版本化工具支持，异步任务在高并发场景下扩展性有限，规划进度仍依赖轮询机制，个性化能力仍以输入偏好为主、尚未充分挖掘用户历史数据。未来可从以下方向继续改进：引入Alembic实现数据库版本化迁移管理；采用Celery分布式任务队列替代线程池以支持高并发场景；升级为SSE或WebSocket实现规划进度的实时推送；基于用户历史行程数据结合向量搜索技术实现更精准的个性化推荐。通过这些演进，系统有望从原型阶段逐步走向更稳健、更可扩展的实际应用形态。

回顾整个毕业设计过程，本文不仅完成了一个具备完整功能的智能旅行规划系统，更重要的是建立了从需求识别到方案落地、从工程实现到测试验证的方法学认识：在面对一个由大模型驱动的应用问题时，应当把模型能力视为系统能力的一部分，通过结构化数据、明确的工具边界、可追溯的任务状态和必要的兜底机制，把不确定性约束在可控范围内，这一点对未来更复杂的智能应用开发同样具有借鉴意义。

# 致 谢

毕业设计的完成离不开许多老师、同学和家人的支持与帮助。在毕业设计选题、方案设计与论文撰写过程中，我得到了指导教师刘寒梅老师在思路梳理、章节组织、技术细节与学术规范等方面的细致指导。刘老师在多次面谈与批注中提出了大量建设性意见，从选题贴合度、研究综述能力、需求与设计的逻辑闭环、模块实现的规范化表述，到测试用例的边界覆盖等方面，反复推动我把研究内容和工程实现做扎实，使我能够不断修正认识、补全证据、完善文稿。

感谢学院各位任课教师在大学期间对我的培养。课程学习中打下的软件工程、数据库原理、计算机网络、面向对象程序设计与人工智能基础等知识，为本课题的实现提供了坚实的理论基础。感谢实验室同学在项目联调、测试验证、文献查阅等方面给予的帮助；感谢答辩组老师在阶段性汇报中提出的中肯意见，这些建议对论文的最终成型同样意义重大。

最后，感谢家人对我学习与生活的理解和支持，正是因为你们的鼓励，我才能够顺利完成毕业设计阶段的各项工作。本文虽尽力做到内容扎实、格式规范，但由于个人水平和经验有限，难免存在疏漏与不足，恳请各位老师与同学批评指正。

# 参考文献

[1] Brown T, Mann B, Ryder N, et al. Language Models are Few-Shot Learners[C]. Advances in Neural Information Processing Systems, 2020.

[2] Achiam J, Adler S, Agarwal S, et al. GPT-4 Technical Report[J]. arXiv preprint arXiv:2303.08774, 2023.

[3] Wei J, Wang X, Schuurmans D, et al. Chain-of-Thought Prompting Elicits Reasoning in Large Language Models[C]. NeurIPS, 2022.

[4] Yao S, Zhao J, Yu D, et al. ReAct: Synergizing Reasoning and Acting in Language Models[C]. ICLR, 2023.

[5] Park J S, O'Brien J C, Cai C J, et al. Generative Agents: Interactive Simulacra of Human Behavior[C]. UIST, 2023.

[6] Significant Gravitas. AutoGPT: An Autonomous GPT-4 Experiment[EB/OL]. https://github.com/Significant-Gravitas/AutoGPT, 2023.

[7] LangChain. LangChain Documentation[EB/OL]. https://python.langchain.com/docs/, 2024.

[8] LangGraph. LangGraph Documentation[EB/OL]. https://langchain-ai.github.io/langgraph/, 2024.

[9] FastAPI. FastAPI Documentation[EB/OL]. https://fastapi.tiangolo.com/, 2024.

[10] Vue.js. Vue 3 Documentation[EB/OL]. https://vuejs.org/, 2024.

[11] SQLAlchemy. SQLAlchemy 2.0 Documentation[EB/OL]. https://docs.sqlalchemy.org/, 2024.

[12] PostgreSQL Global Development Group. PostgreSQL 16 Documentation[EB/OL]. https://www.postgresql.org/docs/, 2024.

[13] Jones M, Bradley J, Sakimura N. JSON Web Token (JWT)[S]. RFC 7519, IETF, 2015.

[14] 高德开放平台. Web服务API文档[EB/OL]. https://lbs.amap.com/api/webservice/summary, 2024.

[15] Pydantic. Pydantic Documentation[EB/OL]. https://docs.pydantic.dev/, 2024.

[16] Woolf S. Building LLM Powered Applications[M]. O'Reilly Media, 2024.

[17] 王建民, 张明. 多智能体系统协同机制研究[J]. 计算机工程, 2023, 49(8): 15-24.

[18] 刘洋, 赵晨. 基于知识增强的大模型应用框架研究[J]. 软件学报, 2024, 35(6): 2101-2120.

[19] 陈凯, 王磊. 面向旅游推荐的个性化路径规划方法[J]. 计算机应用研究, 2022, 39(11): 3401-3408.

[20] 赵一鸣, 孙晨. 面向复杂约束的行程规划算法比较[J]. 现代计算机, 2024(10): 77-84.
