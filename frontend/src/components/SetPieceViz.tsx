import React, { useEffect, useRef } from "react";
import * as THREE from "three";

export default function SetPieceViz() {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!mountRef.current) return;

    const width = mountRef.current.clientWidth;
    const height = 220;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#0a1328");

    const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
    camera.position.set(0, 8, 12);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    const light = new THREE.DirectionalLight(0xffffff, 0.9);
    light.position.set(5, 10, 7);
    scene.add(light);

    const ambient = new THREE.AmbientLight(0x3aa3ff, 0.4);
    scene.add(ambient);

    const pitch = new THREE.Mesh(
      new THREE.PlaneGeometry(14, 9),
      new THREE.MeshStandardMaterial({ color: 0x0b3b2e })
    );
    pitch.rotation.x = -Math.PI / 2;
    scene.add(pitch);

    const lineMaterial = new THREE.LineBasicMaterial({ color: 0x59d5ff });
    const lineGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-7, 0.01, 0),
      new THREE.Vector3(7, 0.01, 0)
    ]);
    const midLine = new THREE.Line(lineGeometry, lineMaterial);
    scene.add(midLine);

    const runner = new THREE.Mesh(
      new THREE.SphereGeometry(0.25, 16, 16),
      new THREE.MeshStandardMaterial({ color: 0x38bdf8 })
    );
    runner.position.set(-3, 0.25, -1);
    scene.add(runner);

    const runner2 = new THREE.Mesh(
      new THREE.SphereGeometry(0.25, 16, 16),
      new THREE.MeshStandardMaterial({ color: 0xf97316 })
    );
    runner2.position.set(2, 0.25, 1.5);
    scene.add(runner2);

    let frame = 0;
    const animate = () => {
      frame += 0.01;
      runner.position.x = -3 + Math.sin(frame) * 1.5;
      runner.position.z = -1 + Math.cos(frame) * 0.6;
      runner2.position.x = 2 + Math.cos(frame) * 1.2;
      runner2.position.z = 1.5 + Math.sin(frame) * 0.4;
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      renderer.dispose();
      if (mountRef.current) {
        mountRef.current.innerHTML = "";
      }
    };
  }, []);

  return (
    <div className="glass rounded-2xl p-4 border border-white/10">
      <h3 className="text-sm font-semibold text-white">Set-Piece Simulation</h3>
      <p className="text-xs text-slate-300/70 mt-1">Animated routine preview</p>
      <div ref={mountRef} className="mt-4 rounded-xl overflow-hidden" />
    </div>
  );
}
