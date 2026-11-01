"""CAP analysis for observed frequency measurements; no acquisition or calibration."""
import csv,math,statistics,sys
from pathlib import Path

def summarize(path, target=1000.0):
    if not math.isfinite(target) or target<=0: raise ValueError("Nominal target must be positive and finite")
    values=[]
    with Path(path).open(newline="",encoding="utf-8-sig") as fh:
        table=csv.DictReader(fh)
        if not table.fieldnames or "reading_hz" not in table.fieldnames:
            raise ValueError("CSV requires a reading_hz column")
        for lineno,row in enumerate(table,2):
            if None in row: raise ValueError(f"CSV row {lineno}: too many fields")
            s=(row.get("reading_hz") or "").strip()
            if not s: raise ValueError(f"CSV row {lineno}: blank measurement")
            try: x=float(s)
            except ValueError as e: raise ValueError(f"CSV row {lineno}: invalid number") from e
            if not math.isfinite(x) or x<0: raise ValueError(f"CSV row {lineno}: nonfinite or negative value")
            values.append(x)
    if not values: raise ValueError("No actual measurements recorded")
    mean=statistics.mean(values)
    return {"n":len(values),"mean_hz":mean,"min_hz":min(values),"max_hz":max(values),
            "range_hz":max(values)-min(values),"sample_stdev_hz":statistics.stdev(values) if len(values)>1 else 0.0,
            "difference_from_nominal_hz":mean-target,"difference_pct":100*(mean-target)/target}

if __name__=='__main__':
    if len(sys.argv) not in (2,3): raise SystemExit("Usage: python cap_analyze.py measurements.csv [nominal_hz]")
    result=summarize(sys.argv[1],float(sys.argv[2]) if len(sys.argv)==3 else 1000.0)
    for k,v in result.items(): print(f"{k}: {v:.5f}" if isinstance(v,float) else f"{k}: {v}")
