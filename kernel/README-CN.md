# Myron 原生内核构建接入

此分支将 Image、内核模块和模块安装交还 Evolution/Lineage 的标准 kernel.mk。
设备层不再关闭原生内核构建器，不再调用 Kleaf 工作区、prepare/migrate 或自定义
内核编译入口，也不需要 MYRON_DT_MODE、MYRON_KERNEL_JOBS、MYRON_KERNEL_RAM_MB。
构建提示来自 ROM 原有规则。

三个 repo 项目为：

- kernel/xiaomi/sm8850：ACK、平台驱动、正常 Kconfig/Makefile。
- kernel/xiaomi/sm8850-modules：68 个外置驱动的原生 Kbuild。
- kernel/xiaomi/sm8850-devicetrees：与 R123 保持一致的设备 DTS。

BoardConfig 使用 TARGET_KERNEL_SOURCE、TARGET_KERNEL_CONFIG、
TARGET_KERNEL_EXT_MODULE_ROOT、TARGET_KERNEL_EXT_MODULES。所有产物由标准
O= 输出目录承载；不添加源码可写白名单，不在编译时下载源码。

## 同步

新工作区可以使用本设备分支及 evolution.dependencies。现有工作区先保留本地
设备树、sepolicy 和其他未提交修改，再合并本分支相对 f6e14d1 的提交。
不要用旧 myron-r123-local-setup.py 重新覆盖这些原生规则。

已有 kernel/xiaomi/sm8850* manifest 项目时直接修改原项目 revision，避免重复路径。
没有这些项目时可复制 kernel/local_manifest.xml，然后正常同步：

```sh
repo sync -c -j4 kernel/xiaomi/sm8850 kernel/xiaomi/sm8850-modules kernel/xiaomi/sm8850-devicetrees
```

旧 manifest 中的 kernel/xiaomi/myron-build 项目及 myron-prebuilt 已不作为本设备
的编译依赖。旧工作区可先保留作为备份；无需迁移它的内部目录，也不要混入新源码树。
这些分支仍处于原生集成验证阶段，必须使用与验证记录对应的版本。

## 编译

保持你现有的 lunch 组合和 OUT_DIR 设置即可。首次从旧适配器切换时建议选择新的
OUT_DIR，以隔离旧模块和镜像的安装残留；这不是日常构建的必需参数。

```sh
source build/envsetup.sh
# 使用现有可用的 lineage_myron lunch 组合
m kernel
m bootimage vendorbootimage recoveryimage dtbimage dtboimage systemdlkmimage vendordlkmimage
m evolution
```

第一条只验证内核构建；第二条生成配套分区；第三条构建完整 Evolution ROM。
继续使用 ROM 自身的并行度和工具链配置，不额外定义 myron 专用内存/线程参数。
不要把主机验证用的 Clang 19 工具路径带入你的 ROM 源码。

## DT 和模块打包

DT 编译使用正常 dtbs 目标。设备仍通过 kernel.mk 提供的 BOARD_CUSTOM_DTBIMG_MK /
BOARD_CUSTOM_DTBOIMG_MK 接口装配镜像：source_dt.py 仅处理已经编译的 DT 输入，
保留 R123 的八个基底、板级 overlay、选择 ID、提供者检查和 FastRPC 子节点顺序。
它不编译内核、不管理源码或工作区。直接改用通用合并顺序尚未完成等价性验证。

kernel.mk 负责 modules_install、depmod 和各分区复制。保留原模块加载列表，并通过
PRODUCT_COPY_FILES 安装 options machine_dlkm myron_tfa_links=1，避免丢失音频选项。
vendor_dlkm 保持 EROFS lz4hc,9。

## 验证边界

Image、338 个树内模块及全部 68 个外置模块已经过主机编译；只读源码目录测试、
modules_install、完整符号/版本检查及标准 ROM 模块打包宏测试已通过。
原来的 297 个已验证模块全部存在，额外 GKI 模块不会自动加入 modules.load。
测试主机缺少 Rust/pahole，没有据此证明生产工具链、完整 ROM 或新内核真机启动成功。
R123 的真机功能结论只属于原构建，不自动延伸到此次原生迁移。

## 2026-11-25 温控模块接入

内核已选择的 `qcom-spmi-temp-alarm`、`qti_cpufreq_cdev`、
`qti_devfreq_cdev`、`qti_userspace_cdev`、`qti_dynamic_hw_trip` 现加入
正常 Android 的 vendor 模块加载清单。原有 SCMI、IPC logging 和 PMIC
提供者仍由第一阶段加载；依赖信息由标准 modules_install/depmod 生成。

`modules.json` 是早期导出的模块清单和历史依赖记录；新增源代码模块的
实际构建/加载选择以 `modules.mk` 与当前 Kconfig 为准。不要使用旧清单
重建并覆盖当前加载列表。此变更需要重新生成并刷入配套 `vendor_dlkm`，
仅更新 `boot` 不会安装新增模块。

这补齐了加载接入，不代表 thermal HAL 配置、`conn_therm` 绑定及 SCMI
固件调用已通过实机验证。保留原厂阈值，不关闭温控保护。

本轮无线事件队列修复见内核提交
[`238cabb9740f`](https://github.com/yuwenhua653/android_kernel_xiaomi_sm8850/commit/238cabb9740f19d3f2495af26f2ec0f6dd4e69b6)。
编译内核后可检查实际配置、ARM64 对象及展开后的加载列表：

```sh
python3 device/xiaomi/myron/kernel/check_thermal_modules.py \
  --kernel-out "$OUT_DIR/target/product/myron/obj/KERNEL_OBJ"
```

该检查不替代完整镜像打包、模块加载和实机温控验证。
