"""Render the report equations as LaTeX (matplotlib mathtext) PNGs for embedding."""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import config as C

EQDIR = os.path.join(C.OUT_DIR, "eq")
EQS = {
    "damage":  r"$D(T)=\sum_{c} f_{c}(h)\,a$",
    "aed":     r"$\mathrm{AED}=\int_{0}^{1} D(p)\,dp\;\approx\;\sum_{i}\frac{1}{2}(D_i+D_{i+1})(p_i-p_{i+1})$",
    "avoided": r"$\mathrm{Avoided\ damage}=\mathrm{AED}_{\mathrm{baseline}}-\mathrm{AED}_{\mathrm{scheme}}$",
    "npv":     r"$\mathrm{NPV}=\sum_{t=1}^{n}\dfrac{B-M}{(1+r)^{t}}\;-\;C_{0}$",
    "bcr":     r"$\mathrm{BCR}=\dfrac{\mathrm{PV(benefits)}}{C_{0}+\mathrm{PV(maintenance)}}$",
    "eape":    r"$\mathrm{EAPE}=\int_{0}^{1} N(p)\,dp$",
    "hr":      r"$\mathrm{HR}=d\,(v+0.5)+DF$",
}


def main():
    os.makedirs(EQDIR, exist_ok=True)
    for name, tex in EQS.items():
        fig = plt.figure(figsize=(0.1, 0.1))
        fig.text(0, 0, tex, fontsize=17, color="#1a1a1a")
        out = os.path.join(EQDIR, f"eq_{name}.png")
        fig.savefig(out, dpi=200, transparent=True, bbox_inches="tight", pad_inches=0.06)
        plt.close(fig)
    print("equations written to", EQDIR)


if __name__ == "__main__":
    main()
