import { useMemo, useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";

// Palette pulled straight from landing.css design tokens.
const FOREST = "#2d6a4f";
const MINT = "#74c69d";
const AMBER = "#fbbf24";

const RUNGS = 28;
const RADIUS = 1.55;
const Y_STEP = 0.3;
const TURN = 0.48; // radians of twist per base pair

interface HelixProps {
  /** South Asian ancestry fraction, 0..1. Drives how much of the panel lights amber. */
  mix: number;
}

function Strands({ mix }: HelixProps) {
  const group = useRef<THREE.Group>(null);
  const { pointer } = useThree();

  const rungs = useMemo(() => {
    const arr: { i: number; y: number; angle: number }[] = [];
    for (let i = 0; i < RUNGS; i++) {
      arr.push({
        i,
        y: (i - (RUNGS - 1) / 2) * Y_STEP,
        angle: i * TURN,
      });
    }
    return arr;
  }, []);

  // Visual-only: more South Asian enrolment concentrates the "at-risk" base pairs.
  // The quantitative claim lives in the readout beside the canvas, not here.
  const amberEvery = Math.max(2, Math.round(RUNGS / (4 + mix * 6)));

  useFrame((_, delta) => {
    const g = group.current;
    if (!g) return;
    g.rotation.y += delta * 0.5;
    const targetX = pointer.y * 0.4;
    const targetZ = pointer.x * 0.3;
    g.rotation.x += (targetX - g.rotation.x) * 0.05;
    g.rotation.z += (targetZ - g.rotation.z) * 0.05;
  });

  return (
    <group ref={group} scale={1.12}>
      {rungs.map(({ i, y, angle }) => {
        const x = Math.cos(angle) * RADIUS;
        const z = Math.sin(angle) * RADIUS;
        const atRisk = i % amberEvery === 0;
        return (
          <group key={i}>
            <mesh position={[x, y, z]}>
              <sphereGeometry args={[0.17, 24, 24]} />
              <meshStandardMaterial
                color={FOREST}
                roughness={0.3}
                metalness={0.15}
                emissive={FOREST}
                emissiveIntensity={0.18}
              />
            </mesh>
            <mesh position={[-x, y, -z]}>
              <sphereGeometry args={[0.17, 24, 24]} />
              <meshStandardMaterial
                color={MINT}
                roughness={0.3}
                metalness={0.15}
                emissive={MINT}
                emissiveIntensity={0.22}
              />
            </mesh>
            <mesh position={[0, y, 0]} rotation={[0, -angle, 0]}>
              <boxGeometry args={[RADIUS * 2, 0.06, 0.06]} />
              <meshStandardMaterial
                color={atRisk ? AMBER : MINT}
                emissive={atRisk ? AMBER : FOREST}
                emissiveIntensity={atRisk ? 0.7 : 0.1}
                roughness={0.45}
              />
            </mesh>
          </group>
        );
      })}
    </group>
  );
}

export function DnaHelix({ mix }: HelixProps) {
  return (
    <Canvas
      camera={{ position: [0, 0, 5.5], fov: 38 }}
      gl={{ alpha: true, antialias: true }}
      dpr={[1, 2]}
      onCreated={() => {
        // Guarantee the drawing buffer matches the container even if the
        // ResizeObserver misses the initial layout (seen after lazy mount).
        requestAnimationFrame(() => window.dispatchEvent(new Event("resize")));
      }}
    >
      <ambientLight intensity={0.75} />
      <directionalLight position={[4, 6, 5]} intensity={1.15} />
      <pointLight position={[-4, -2, 3]} intensity={0.6} color={MINT} />
      <Strands mix={mix} />
    </Canvas>
  );
}
