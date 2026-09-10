export function blendCurves(size=129){
 const a=new Float32Array(size),b=new Float32Array(size),lowA=new Float32Array(size),lowB=new Float32Array(size);
 for(let i=0;i<size;i++){const p=i/(size-1);a[i]=Math.cos(p*Math.PI/2);b[i]=Math.sin(p*Math.PI/2);lowA[i]=Math.max(-24,20*Math.log10(Math.max(a[i],1e-8)));lowB[i]=Math.max(-24,20*Math.log10(Math.max(b[i],1e-8)));}
 a[size-1]=0;b[0]=0;return {a,b,lowA,lowB};
}
