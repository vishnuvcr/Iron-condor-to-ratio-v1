from pathlib import Path
import tempfile

from phase1_g6_source_acquisition import acquire_one, sha256

def main():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "source.html"
        payload = b"immutable-source-bytes"
        expected = sha256(payload)
        p.write_bytes(payload)

        status, meta = acquire_one(
            {"url": "https://example.invalid/source", "expected_sha256": expected},
            p,
        )
        assert status == "CACHE_HIT_VALIDATED"
        assert meta["sha256"] == expected

        p.write_bytes(b"tampered")
        try:
            acquire_one(
                {"url": "https://example.invalid/source", "expected_sha256": expected},
                p,
            )
        except RuntimeError as exc:
            assert "CACHE_DIGEST_MISMATCH" in str(exc)
        else:
            raise AssertionError("digest mismatch was not rejected")

        p.write_bytes(payload)
        try:
            acquire_one(
                {"url": "https://example.invalid/source"},
                p,
            )
        except RuntimeError as exc:
            assert "CACHE_PROVENANCE_UNVERIFIED" in str(exc)
        else:
            raise AssertionError("missing expected digest was not rejected")

if __name__ == "__main__":
    main()
