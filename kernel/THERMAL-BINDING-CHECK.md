# Connector thermal binding checks

`source_dt.py` checks `required_thermal_bindings` after merging each base with
the final board overlay and before emitting ROM input images. Both connector
zones must reference the reviewed ADC provider and their exact channel IDs;
provider/channel/ancestor status, one-cell sensor arguments, unique phandles,
unique channels and thermal-monitor mode must be valid. Compiler-assigned
phandle numbers are resolved rather than pinned.

The eight archived merged phone DT variants pass. This adds verification;
it does not change sensor names or DT data and does not prove current-device
probe success. Run the mutation regression with:

```
python3 -B -m unittest discover -s device/xiaomi/myron/kernel -p 'test_*.py'
```

Paired kernel checkpoint:
[232f1e875744](https://github.com/yuwenhua653/android_kernel_xiaomi_sm8850/commit/232f1e8757440841e61783f4831dc5ad1b46f279).
The kernel includes corrected sensor-before-GPIO probe ordering. Its
`android/myron-native/runtime-gap-followup-20261125.md` records the outstanding
Xiaomi thermal_message interface gap. QTI module load-list checks alone are not
full thermal-policy qualification. Libperfmgr is deferred; no shared ROM build
rules are changed and this checkpoint is not a compile/flash request.
