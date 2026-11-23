#
# Copyright (C) 2026 The Android Open Source Project
#
# SPDX-License-Identifier: Apache-2.0
#

DEVICE_PATH := device/xiaomi/myron

# Inherit from sm8850-common
include device/xiaomi/sm8850-common/BoardConfigCommon.mk

# Inherit miuicam
include device/xiaomi/myron-miuicamera/BoardConfig.mk

# Display
TARGET_SCREEN_DENSITY := 520

# Native kernel and modules built by the ROM kernel.mk.
include $(DEVICE_PATH)/kernel/BoardConfigKernel.mk

TARGET_ODM_PROP += $(DEVICE_PATH)/configs/properties/odm.prop
TARGET_VENDOR_PROP += $(DEVICE_PATH)/configs/properties/vendor.prop

# Label the CIT collision switch with the existing sensor property type.
BOARD_VENDOR_SEPOLICY_DIRS += $(DEVICE_PATH)/sepolicy/vendor

# Platform
BOOT_SECURITY_PATCH := $(PLATFORM_SECURITY_PATCH)
VENDOR_SECURITY_PATCH := $(PLATFORM_SECURITY_PATCH)

# Inherit from the proprietary version
include vendor/xiaomi/myron/BoardConfigVendor.mk

BOARD_VENDOR_DLKMIMAGE_FILE_SYSTEM_TYPE := erofs
BOARD_VENDOR_DLKMIMAGE_EROFS_COMPRESSOR := lz4hc,9
TARGET_USERIMAGES_SPARSE_EROFS_DISABLED := true

# BEGIN MYRON CAMERA POLICY INTEGRATION 20261117
# Include the camera policy even when only its APK product is inherited.
ifeq ($(filter device/xiaomi/myron-miuicamera/sepolicy/vendor,$(BOARD_VENDOR_SEPOLICY_DIRS)),)
BOARD_VENDOR_SEPOLICY_DIRS += device/xiaomi/myron-miuicamera/sepolicy/vendor
endif
ifeq ($(filter device/xiaomi/myron-miuicamera/sepolicy/public,$(SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS)),)
SYSTEM_EXT_PUBLIC_SEPOLICY_DIRS += device/xiaomi/myron-miuicamera/sepolicy/public
endif
ifeq ($(filter device/xiaomi/myron-miuicamera/sepolicy/private,$(SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS)),)
SYSTEM_EXT_PRIVATE_SEPOLICY_DIRS += device/xiaomi/myron-miuicamera/sepolicy/private
endif
# END MYRON CAMERA POLICY INTEGRATION 20261117
