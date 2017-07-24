#!/bin/bash

set -o errexit -o nounset -o noclobber -o pipefail

setSetting() {
    FILE="$1"
    SETTING="$2"
    VALUE="$3"

    sed -Ei 's/^('"$SETTING"'[[:space:]]*=[[:space:]]*)[0-9.]+/\1'"$VALUE"'/m' "$FILE"
}

# Disable outputting live simulation results in a window
setSetting "_defaults" "dovis" 0
sed -i 's/ plt.show()/ #plt.show()/' analysis/plotvar.py

rm -f *.h5

# Advection simulations
for SOLVER in advection advection_rk; do
    for INPUT in smooth tophat; do
        for LIMITER in 0 1 2; do
            for CFL in $(seq 0.1 0.01 1.5); do
                OUT_DIR="../output/$SOLVER-$INPUT-$LIMITER-$CFL"
                if [ -d "$OUT_DIR" ]; then
                    continue
                fi
                mkdir -p "$OUT_DIR"

                echo -n "($SOLVER, $INPUT, $LIMITER, $CFL): "
                setSetting "$SOLVER/problems/inputs.$INPUT" "cfl" "$CFL"
                setSetting "$SOLVER/problems/inputs.$INPUT" "limiter" "$LIMITER"

                ./pyro.py "$SOLVER" "$INPUT" "inputs.$INPUT" > "$OUT_DIR/log" 2>&1
                mv *.h5 "$OUT_DIR/"

                OUTPUTS=("$OUT_DIR"/*.h5)
                analysis/smooth_error.py "${OUTPUTS[-1]}" |& grep error | awk '{print $6}'
                analysis/plotvar.py "${OUTPUTS[-1]}" density -o "$OUT_DIR/out.png"
            done
        done
    done
done

# Diffusion simulations
setSetting "diffusion/problems/inputs.gaussian" "dt_out" "0.00001"
for K in 0.5 1.0 1.5; do
    OUT_DIR="../output/diffusion-gaussian-$K"
    rm -rf "$OUT_DIR"
    mkdir -p "$OUT_DIR"

    setSetting "diffusion/problems/inputs.gaussian" "k" "$K"
    ./pyro.py diffusion gaussian inputs.gaussian > "$OUT_DIR/log" 2>&1
    mv *.h5 "$OUT_DIR/"
done

# Blast wave simulations
setSetting "compressible/problems/inputs.sedov" "dt_out" "0.00001"
for LIMITER in 0 1 2; do
    for CVISC in 0.001 0.1 10; do
        OUT_DIR="../output/blast-$LIMITER-$CVISC"
        rm -rf "$OUT_DIR"
        mkdir -p "$OUT_DIR"

        setSetting "compressible/problems/inputs.sedov" "limiter" "$LIMITER"
        setSetting "compressible/problems/inputs.sedov" "cvisc" "$CVISC"
        ./pyro.py compressible sedov inputs.sedov > "$OUT_DIR/log" 2>&1
        mv *.h5 "$OUT_DIR/"
    done
done
