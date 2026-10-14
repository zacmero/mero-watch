# Custom-screen compatibility candidate

`mero-screen-test.res` is a single-image BR28/RU30 background generated from our own `docs/mockups/custom-background-test.svg`. The `SCREEN TEST` label and drawn navigation identify an appearance test; the image supplies no executable code, live status or touch handlers.

- Dimensions: 240 × 296.
- Encoded bytes: 27,993.
- SHA-256: `e5159492a76ffeea541c3c583860b3b1c920e0d6ad9e9ec62861b03c718e89e6`.
- Source: GFit Pro's locally extracted `libjl_bmp_convert.so`, executed offline by `scripts/br28_converter_oracle.py`.
- Converter SHA-256: `70c859271d153093b379356102ae32257f5ea36558b9775756660db21958a5f4`.
- Independent decoder verifies record/image checksums and the complete pixel image. Exact screen layout after installation is still under test; the selected vendor face may overlay clock/widgets.

`mero-screen-test.png` is decoded from this native-generated resource. It can be selected through GFit Pro's photo-background picker, whose availability the owner has now confirmed. The app performs its own conversion and transfer; this does not test direct computer-to-watch resource transfer.

Reproduce offline, using the inspected library extracted locally from GFit's architecture APK split:

```bash
rtk proxy .venv/bin/python -m pip install -r requirements-analysis.txt
rtk proxy rsvg-convert -o /tmp/mero-screen-source.png docs/mockups/custom-background-test.svg
rtk proxy .venv/bin/python scripts/br28_converter_oracle.py \
  --library /absolute/private/libjl_bmp_convert.so \
  /tmp/mero-screen-source.png /tmp/mero-screen-test.res
rtk proxy .venv/bin/python scripts/ru30_background.py \
  decode /tmp/mero-screen-test.res /tmp/mero-screen-preview.png
```

The converter binary is not redistributed. The public Python encoder produces the same supported image layout and decoded pixels, but its compression grouping differs from the native converter on the full screen. The checked-in candidate uses the native converter output.
