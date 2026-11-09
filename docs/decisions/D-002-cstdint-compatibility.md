# D-002 — Add explicit `<cstdint>` includes to legacy headers

- **Date:** 2026-11-08
- **Status:** Accepted; applied locally
- **Context:** ns-3.35 failed to compile because three headers used `uint8_t` without including the standard header that defines it.
- **Alternatives:** Add broad compiler flags/precompiled includes; alter protocol type declarations; use newer source/port the NR-U module; add the direct header dependency.
- **Selected:** Add `<cstdint>` to bit serializer, bit deserializer, and Wi-Fi block-ack type headers.
- **Reasoning:** Complete compiler diagnostics identified the undeclared `uint8_t`; all subsequent constructor/member diagnostics cascaded from the type failing to parse. The direct include is the minimal source-level fix and changes no runtime/protocol logic.
- **Consequences:** Source tree is locally patched; new checkouts must apply the patch before building.
- **Disadvantages:** It is a local maintenance delta from upstream. It must remain visible and reproducible.
- **Evidence:** [`patches/ns-3.35-gcc-fixed-width-includes.patch`](../../patches/ns-3.35-gcc-fixed-width-includes.patch), `logs/build.log`, `logs/build-resume-1.log`.
