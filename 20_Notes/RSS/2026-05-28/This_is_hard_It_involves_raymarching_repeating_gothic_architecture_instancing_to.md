---
title: "This is hard! It involves raymarching repeating gothic architecture (instancing towers across an infinite grid with gothic silhouettes and windows), a displaced ocean surface with believable wave motion, and stormy atmospheric lighting/fog to tie it together... and doing this all with no textures or external assets, just math.

Here is the full code:

/*  D R O W N E D   C A T H E D R A L   C I T Y   ·  mk2   —   (classic)  */
precision highp float;
uniform vec2 resolution;
uniform vec2 mouse;
uniform float time;

#define CITY_STEPS  90
#define WATER_STEPS 60
#define REFL_STEPS  20
#define VOL_STEPS   18
#define FAR  200.0
#define CELL 8.0
#define CREST_K     2.2     // wave crest sharpness (1 = round sine, higher = choppier)
#define WIN_LIT     0.46    // fraction of windows lit (lower = more lit)
#define BEAM_BRIGHT 0.07    // lighthouse beam intensity
#define BEAM_SPEED  0.50    // beam rotation speed
const vec3 SUN = vec3(-0.548, 0.685, -0.480);

/* ---------- hash / noise ---------- */
float hash21(vec2 p){ p=fract(p*vec2(123.34,345.45)); p+=dot(p,p+34.345); return fract(p.x*p.y); }
float hash11(float n){ return fract(sin(n)*43758.5453123); }
float noise(vec2 p){
    vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
    return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),
               mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x),f.y);
}
float fbm(vec2 p){
    float v=0.0,a=0.5; mat2 m=mat2(1.6,1.2,-1.2,1.6);
    for(int i=0;i<4;i++){ v+=a*noise(p); p=m*p; a*=0.5; } return v;
}

/* ---------- ocean ---------- */
float crest(float s){ float u=0.5+0.5*s; u=pow(u,CREST_K); return u*2.0-1.0; }
float oceanLow(vec2 p){
    float t=time, h=0.0;
    h += 0.95*crest(sin(dot(p,vec2( 0.16, 0.11))+t*1.10));
    h += 0.70*crest(sin(dot(p,vec2(-0.12, 0.21))-t*0.90));
    h += 0.50*crest(sin(dot(p,vec2( 0.09,-0.17))+t*0.75));
    h += 0.30*crest(sin(dot(p,vec2( 0.23, 0.06))+t*1.35));
    return h;
}
float oceanHigh(vec2 p){
    float h=oceanLow(p);
    h += (fbm(p*0.35+vec2(0.0,time*0.18))-0.5)*0.75;
    h += (fbm(p*0.90-vec2(time*0.16,0.0))-0.5)*0.30;
    h += (fbm(p*2.10+vec2(time*0.25,0.0))-0.5)*0.12;
    return h;
}

/* ---------- sdf ---------- */
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.0))+min(max(q.x,max(q.y,q.z)),0.0); }
float sdCappedCone(vec3 p, float h, float r1, float r2){
    vec2 q=vec2(length(p.xz),p.y);
    vec2 k1=vec2(r2,h), k2=vec2(r2-r1,2.0*h);
    vec2 ca=vec2(q.x-min(q.x,(q.y<0.0)?r1:r2),abs(q.y)-h);
    vec2 cb=q-k1+k2*clamp(dot(k1-q,k2)/dot(k2,k2),0.0,1.0);
    float s=(cb.x<0.0&&ca.y<0.0)?-1.0:1.0;
    return s*sqrt(min(dot(ca,ca),dot(cb,cb)));
}
float towerSDF(vec3 p){
    vec2 cid=floor(p.xz/CELL);
    vec2 local=mod(p.xz,CELL)-0.5*CELL;
    vec3 q=vec3(local.x,p.y,local.y);
    float r0=hash21(cid), r1=hash21(cid+5.7);
    float halfW=0.85+r1*0.75;
    float botY=-9.0, topY, spireH;
    if(r0<0.18){ topY=-5.0; spireH=0.0; }
    else       { topY=1.0+r0*15.0; spireH=2.0+r1*5.5; }
    float cy=0.5*(botY+topY), halfH=0.5*(topY-botY);
    float s1=sdBox(q-vec3(0.0,cy,0.0),vec3(halfW,      halfH,halfW*0.55));
    float s2=sdBox(q-vec3(0.0,cy,0.0),vec3(halfW*0.55, halfH,halfW));
    float d=min(s1,s2);
    if(spireH>0.0){
        d=min(d,sdCappedCone(q-vec3(0.0,topY+spireH*0.5,0.0),spireH*0.5,halfW*1.0,0.04));
        float pin=1.0+r1*1.6;                                   // 4 corner pinnacles (abs-mirrored)
        vec3 qc=vec3(abs(q.x)-halfW*0.72, q.y-(topY+pin*0.5), abs(q.z)-halfW*0.72);
        d=min(d,sdCappedCone(qc,pin*0.5,0.16,0.02));
    }
    return d;
}
vec3 calcNormal(vec3 p){
    vec2 e=vec2(0.01,0.0);
    return normalize(vec3(towerSDF(p+e.xyy)-towerSDF(p-e.xyy),
                          towerSDF(p+e.yxy)-towerSDF(p-e.yxy),
                          towerSDF(p+e.yyx)-towerSDF(p-e.yyx)));
}
vec3 waterNormal(vec3 p){
    float e=0.10, h=oceanHigh(p.xz);
    return normalize(vec3(h-oceanHigh(p.xz+vec2(e,0.0)), e, h-oceanHigh(p.xz+vec2(0.0,e))));
}

/* ---------- gothic window: pointed (equilateral) arch + tracery + glow ---------- */
vec3 windowField(vec2 f){                 // f in [-0.5,0.5]; returns (pane, glow, glassArea)
    float halfW=0.30, bottom=-0.42, sh=0.02, A=0.38, e=0.012;
    float c=(A*A-halfW*halfW)/(2.0*halfW), R=halfW+c;
    float rx=smoothstep(halfW,halfW-e,abs(f.x));
    float ry=smoothstep(bottom-e,bottom,f.y)*smoothstep(sh,sh-e,f.y);
    float rect=rx*ry;
    float dl=(f.x+c)*(f.x+c)+(f.y-sh)*(f.y-sh);
    float dr=(f.x-c)*(f.x-c)+(f.y-sh)*(f.y-sh);
    float arch=smoothstep(R*R,R*R-0.02,max(dl,dr))*smoothstep(sh-e,sh,f.y);
    float glassA=clamp(max(rect,arch),0.0,1.0);
    float mull=smoothstep(0.018,0.030,abs(f.x));                // mullion
    float tran=smoothstep(0.016,0.028,abs(f.y-(sh-0.18)));      // transom
    float pane=glassA*min(mull,tran);
    float gr=length(vec2(f.x/0.34,f.y/0.42));
    return vec3(pane, exp(-gr*gr*1.3), glassA);
}

/* ---------- storm: full-scene flash + forked bolt event ---------- */
vec3 stormStrike(){          // (flashIntensity, boltX, boltLife)
    float t=time, flash=0.0, bx=0.0, blife=0.0;
    for(int i=0;i<3;i++){
        float fi=float(i), sp=0.31+fi*0.11, ph=t*sp+fi*7.0, seg=floor(ph);
        if(hash11(seg+fi*23.1)>0.80){
            float fr=fract(ph);
            float env=exp(-fr*12.0)+0.5*exp(-abs(fr-0.08)*20.0)+0.25*exp(-abs(fr-0.16)*18.0);
            env*=0.6+0.4*hash11(seg*1.7+fi);
            flash+=env;
            if(env>blife){ blife=env; bx=(hash11(seg*3.3+fi*5.0)*2.0-1.0)*0.9; }
        }
    }
    return vec3(clamp(flash,0.0,1.5),bx,clamp(blife,0.0,1.0));
}

/* ---------- sky ---------- */
vec3 skyColor(vec3 rd, vec3 strike){
    float fl=strike.x, y=clamp(rd.y,-0.3,1.0);
    vec3 col=mix(vec3(0.090,0.100,0.130),vec3(0.020,0.030,0.050),smoothstep(0.0,0.65,y));
    vec2 sp=rd.xz/(abs(rd.y)+0.20);
    float c1=fbm(sp*0.6+vec2(time*0.015,time*0.006));
    float c2=fbm(sp*1.4-vec2(time*0.010,0.0));
    float clouds=smoothstep(0.45,1.05,c1*0.7+c2*0.5);
    col=mix(col,mix(vec3(0.045,0.055,0.075),vec3(0.120,0.130,0.160),c2),clouds*(1.0-smoothstep(0.0,0.55,y)));
    float md=pow(clamp(dot(rd,normalize(vec3(0.30,0.55,0.60))),0.0,1.0),60.0);
    col+=vec3(0.20,0.22,0.28)*md*(1.0-clouds*0.8);
    col+=fl*mix(vec3(0.35,0.42,0.65),vec3(0.65,0.70,0.95),clouds)
            *(0.30+0.70*clouds)*(0.40+0.60*(1.0-smoothstep(0.0,0.70,y)));
    col+=vec3(0.090,0.100,0.130)*pow(1.0-clamp(abs(rd.y)/0.40,0.0,1.0),3.0)*0.40;
    return col;
}

/* ---------- stone ---------- */
vec3 stoneAlbedo(vec3 p, vec3 n){
    vec3 base=vec3(0.115,0.125,0.140);
    base*=mix(vec3(0.88,0.92,1.0),vec3(1.08,1.0,0.88),hash21(floor(p.xz/CELL)+2.3));
    vec2 suv=(abs(n.x)>abs(n.z))?vec2(p.z,p.y):vec2(p.x,p.y);
    base*=1.0-0.45*(1.0-smoothstep(0.0,0.16,abs(fract(suv.x*2.2+0.5)-0.5)));   // colonettes
    base*=1.0-0.28*(1.0-smoothstep(0.0,0.10,abs(fract(p.y*0.45)-0.5)));        // string courses
    base*=0.72+0.5*fbm(p.xz*0.6+p.y*0.25);                                     // grime
    base*=0.85+0.3*noise(suv*6.0);                                            // fine grain
    return base;
}
vec3 shadeStone(vec3 p, vec3 rd, vec3 strike){
    float flash=strike.x;
    vec3 n=calcNormal(p), alb=stoneAlbedo(p,n);
    float rel=p.y-oceanLow(p.xz);
    float wet=smoothstep(1.6,-0.3,rel);
    float algae=smoothstep(2.4,-0.6,rel)*smoothstep(-1.8,0.4,rel)*(0.5+0.5*fbm(p.xz*1.6+p.y*0.5));
    alb=mix(alb,vec3(0.05,0.11,0.06),clamp(algae*0.7,0.0,1.0));
    alb*=mix(1.0,0.55,wet);
    float dif=clamp(dot(n,SUN),0.0,1.0), sky=clamp(0.5+0.5*n.y,0.0,1.0);
    vec3 col=alb*0.16 + alb*sky*vec3(0.16,0.20,0.28) + alb*dif*vec3(0.5,0.5,0.55);
    float fres=pow(1.0-clamp(dot(n,-rd),0.0,1.0),4.0);
    col+=fres*vec3(0.12,0.15,0.20)*(0.5+0.5*wet);
    float sp=pow(clamp(dot(n,normalize(SUN-rd)),0.0,1.0),mix(30.0,120.0,wet));
    col+=sp*mix(0.15,0.9,wet)*vec3(0.55,0.62,0.72);
    col+=flash*alb*vec3(0.6,0.7,1.0)*(0.3+0.7*dif+0.5*fres);
    // windows
    float faceMask=smoothstep(0.55,0.22,abs(n.y));
    vec2 suv=(abs(n.x)>abs(n.z))?vec2(p.z,p.y):vec2(p.x,p.y);
    vec2 sc=suv/vec2(1.15,1.55), cell=floor(sc), f=fract(sc)-0.5;
    vec2 axisSeed=(abs(n.x)>abs(n.z))?vec2(11.0,3.0):vec2(2.0,17.0);
    vec2 cidp=floor(p.xz/CELL);
    vec3 win=windowField(f);
    float lsel=hash21(cell+cidp*3.7+axisSeed);
    float lit=step(WIN_LIT,lsel);
    vec3 wcol=vec3(1.0,0.60,0.26);
    float v1=hash21(cell+cidp*7.1+axisSeed);
    if(v1>0.90) wcol=vec3(0.45,0.80,1.0); else if(v1>0.82) wcol=vec3(0.5,1.0,0.62);
    float flick=0.78+0.18*sin(time*(2.5+lsel*5.0)+lsel*60.0)+0.06*sin(time*19.0+lsel*200.0);
    float gate=faceMask*smoothstep(-1.0,1.6,p.y)*(1.0-wet*0.7);
    col=mix(col,col*0.30,win.z*gate*(1.0-lit));
    col+=win.z*gate*(1.0-lit)*vec3(0.02,0.03,0.05);
    float e=gate*lit*flick;
    col+=win.x*e*wcol*2.4 + win.y*e*wcol*0.65;
    return col;
}

/* ---------- marchers ---------- */
float marchCity(vec3 ro, vec3 rd){
    float t=0.05;
    for(int i=0;i<CITY_STEPS;i++){ float d=towerSDF(ro+rd*t); if(d<0.002*t) return t; t+=clamp(d,0.02,2.0); if(t>FAR) break; }
    return -1.0;
}
float marchCityRefl(vec3 ro, vec3 rd){
    float t=0.1;
    for(int i=0;i<REFL_STEPS;i++){ float d=towerSDF(ro+rd*t); if(d<0.01*t) return t; t+=clamp(d,0.05,3.0); if(t>80.0) break; }
    return -1.0;
}
float marchWater(vec3 ro, vec3 rd){
    float t=0.05,lastT=t;
    for(int i=0;i<WATER_STEPS;i++){
        vec3 p=ro+rd*t; float h=oceanLow(p.xz);
        if(p.y-h<0.0){
            float a=lastT,b=t;
            for(int j=0;j<6;j++){ float m=0.5*(a+b); vec3 pm=ro+rd*m; if(pm.y-oceanLow(pm.xz)<0.0) b=m; else a=m; }
            return 0.5*(a+b);
        }
        lastT=t; t+=max(0.12,(p.y-h)*0.5); if(t>FAR) break;
    }
    return -1.0;
}

/* ---------- water ---------- */
vec3 shadeWater(vec3 p, vec3 rd, vec3 strike){
    float flash=strike.x;
    vec3 n=waterNormal(p), rfl=reflect(rd,n); rfl.y=max(rfl.y,0.02);
    vec3 rcol; float tr=marchCityRefl(p+n*0.05,rfl);
    if(tr>0.0) rcol=mix(shadeStone(p+rfl*tr,rfl,strike),skyColor(rfl,strike),1.0-exp(-tr*0.06));
    else       rcol=skyColor(rfl,strike);
    float crestH=oceanHigh(p.xz);
    vec3 tcol=vec3(0.012,0.030,0.040)+vec3(0.02,0.10,0.10)*smoothstep(0.4,1.6,crestH); // murk + crest glow
    float fres=0.02+0.98*pow(1.0-clamp(dot(n,-rd),0.0,1.0),5.0);
    vec3 col=mix(tcol,rcol,fres);
    float fn=fbm(p.xz*1.3+time*0.25), fn2=fbm(p.xz*3.0-time*0.4);
    float crestFoam=smoothstep(1.2,2.2,crestH)*smoothstep(0.35,0.85,fn);
    float streak=smoothstep(0.6,0.95,fn2)*smoothstep(0.8,1.6,crestH)*0.5;
    float baseFoam=(1.0-smoothstep(0.0,1.0,towerSDF(vec3(p.x,0.0,p.z))))*(0.5+0.5*fn)*0.9;
    float foam=clamp(max(max(crestFoam,streak),baseFoam),0.0,1.0)*(0.6+0.4*fn2);
    col=mix(col,vec3(0.78,0.82,0.85),foam);
    float spe=pow(clamp(dot(n,normalize(SUN-rd)),0.0,1.0),220.0);
    col+=spe*(0.4+3.0*flash)*vec3(0.8,0.85,1.0);
    col+=flash*fres*vec3(0.3,0.4,0.6);
    return col;
}

/* ---------- volumetrics: sweeping beacon + rain + lightning haze ---------- */
vec3 volumetrics(vec3 ro, vec3 rd, float tmax, vec3 strike){
    float vmax=min(tmax,90.0), dt=vmax/float(VOL_STEPS);
    float t=dt*(0.5+0.5*hash21(gl_FragCoord.xy));
    float ang=time*BEAM_SPEED;
    vec3 bdir=normalize(vec3(cos(ang),-0.16,sin(ang)));
    vec3 bpos=vec3(7.0,23.0,ro.z+34.0), acc=vec3(0.0);
    for(int i=0;i<VOL_STEPS;i++){
        if(t>vmax) break;
        vec3 q=ro+rd*t;
        float rfog=0.010+0.030*exp(-max(q.y+2.0,0.0)*0.10);
        vec3 toq=q-bpos; float along=dot(toq,bdir);
        if(along>0.5){
            vec3 perp=toq-along*bdir;
            float beam=exp(-dot(perp,perp)/(0.6+along*along*0.012))*exp(-along*0.018);
            beam*=0.5+0.9*fbm(q.xz*0.6+q.y*0.4+vec2(0.0,time*1.6));
            beam*=smoothstep(-2.0,16.0,q.y);
            acc+=beam*vec3(1.0,0.92,0.72)*BEAM_BRIGHT*dt;
        }
        acc+=strike.x*rfog*vec3(0.45,0.55,0.80)*0.5*dt;
        acc+=rfog*vec3(0.05,0.06,0.08)*0.3*dt;
        t+=dt;
    }
    return acc;
}

/* ---------- rain / bolt / tonemap ---------- */
float rainLayer(vec2 uv, float sc, float sp){
    uv*=sc; uv.x+=uv.y*0.25; uv.y+=time*sp; uv.x+=floor(uv.y);
    vec2 f=fract(uv);
    return (1.0-smoothstep(0.0,0.06,abs(f.x-0.5)))*smoothstep(0.0,0.2,f.y)*(1.0-smoothstep(0.55,1.0,f.y))*step(0.72,hash21(floor(uv)));
}
float boltGlow(vec2 uv, vec3 strike){
    float life=strike.z; if(life<0.02) return 0.0;
    float bx=strike.y, seedA=bx*7.0+3.1;
    float jit=(fbm(vec2(uv.y*3.5+seedA,seedA))-0.5)*0.6
            +(fbm(vec2(uv.y*11.0+seedA*2.0,seedA*0.7))-0.5)*0.22
            +(fbm(vec2(uv.y*26.0+seedA,seedA*1.3))-0.5)*0.08;
    float xp=bx+jit;
    float g=(0.010/(abs(uv.x-xp)+0.010))*smoothstep(-0.9,0.6,uv.y);
    if(uv.y<0.1){
        float jit2=(fbm(vec2(uv.y*9.0+seedA*3.0,seedA*4.0))-0.5)*0.5;
        g+=(0.006/(abs(uv.x-(xp+(0.1-uv.y)*1.2+jit2))+0.006))*0.6;     // fork
    }
    return g*life*1.4;
}
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0.0,1.0); }

void main(){
    vec2 uv=(gl_FragCoord.xy*2.0-resolution.xy)/resolution.y;
    vec3 strike=stormStrike();
    float ct=time;

    vec3 ro=vec3(0.7*sin(ct*0.25),4.6,ct*3.0);
    ro.y+=oceanLow(ro.xz)*0.30+sin(ct*0.8)*0.18;
    float pitch=-0.9+0.6*sin(ct*0.12);
    vec3 ta=ro+vec3(0.6*sin(ct*0.16),pitch,4.0);
    vec3 f=normalize(ta-ro), r=normalize(cross(vec3(0,1,0),f)), u=cross(f,r);
    float roll=sin(ct*0.45)*0.05+sin(ct*0.21)*0.025;
    vec3 rr=r*cos(roll)+u*sin(roll), uu=u*cos(roll)-r*sin(roll);
    vec3 rd=normalize(uv.x*rr+uv.y*uu+1.25*f);

    float tC=marchCity(ro,rd);
    float tW=(rd.y<0.0)?marchWater(ro,rd):-1.0;

    vec3 col; float dist;
    if(tC>0.0 && (tW<0.0||tC<tW)){ col=shadeStone(ro+rd*tC,rd,strike); dist=tC; }
    else if(tW>0.0)              { col=shadeWater(ro+rd*tW,rd,strike); dist=tW; }
    else                         { col=skyColor(rd,strike);            dist=FAR; }

    col=mix(col,skyColor(rd,strike),1.0-exp(-dist*0.016));            // fog
    col+=volumetrics(ro,rd,dist,strike);                             // beam + rain + haze
    col+=(rainLayer(uv,14.0,16.0)*0.8+rainLayer(uv*1.7,22.0,22.0)*0.5)*0.03*vec3(0.8,0.85,0.95);
    col+=boltGlow(uv,strike)*vec3(0.75,0.82,1.0);                    // visible bolt
    col*=1.04;
    col=mix(col,col*vec3(0.9,1.0,1.04),0.3);                         // cool the shadows
    col*=1.0-0.18*dot(uv,uv);                                        // vignette
    col=aces(col);
    col=pow(col,vec3(0.95));
    gl_FragColor=vec4(col,1.0);
}"
source: "X - Ethan Mollick"
author: "Ethan Mollick"
url: "http://nitter.perennialte.ch/emollick/status/2060043661920919820#m"
published: "Thu, 28 May 2026 17:00:57 GMT"
scanned: "2026-05-28"
tags: [rss, x_-_ethan_mollick, twitter, x, social, ai, ai, dev]
type: social
---

# This is hard! It involves raymarching repeating gothic architecture (instancing towers across an infinite grid with gothic silhouettes and windows), a displaced ocean surface with believable wave motion, and stormy atmospheric lighting/fog to tie it together... and doing this all with no textures or external assets, just math.

Here is the full code:

/*  D R O W N E D   C A T H E D R A L   C I T Y   ·  mk2   —   (classic)  */
precision highp float;
uniform vec2 resolution;
uniform vec2 mouse;
uniform float time;

#define CITY_STEPS  90
#define WATER_STEPS 60
#define REFL_STEPS  20
#define VOL_STEPS   18
#define FAR  200.0
#define CELL 8.0
#define CREST_K     2.2     // wave crest sharpness (1 = round sine, higher = choppier)
#define WIN_LIT     0.46    // fraction of windows lit (lower = more lit)
#define BEAM_BRIGHT 0.07    // lighthouse beam intensity
#define BEAM_SPEED  0.50    // beam rotation speed
const vec3 SUN = vec3(-0.548, 0.685, -0.480);

/* ---------- hash / noise ---------- */
float hash21(vec2 p){ p=fract(p*vec2(123.34,345.45)); p+=dot(p,p+34.345); return fract(p.x*p.y); }
float hash11(float n){ return fract(sin(n)*43758.5453123); }
float noise(vec2 p){
    vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
    return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),
               mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x),f.y);
}
float fbm(vec2 p){
    float v=0.0,a=0.5; mat2 m=mat2(1.6,1.2,-1.2,1.6);
    for(int i=0;i<4;i++){ v+=a*noise(p); p=m*p; a*=0.5; } return v;
}

/* ---------- ocean ---------- */
float crest(float s){ float u=0.5+0.5*s; u=pow(u,CREST_K); return u*2.0-1.0; }
float oceanLow(vec2 p){
    float t=time, h=0.0;
    h += 0.95*crest(sin(dot(p,vec2( 0.16, 0.11))+t*1.10));
    h += 0.70*crest(sin(dot(p,vec2(-0.12, 0.21))-t*0.90));
    h += 0.50*crest(sin(dot(p,vec2( 0.09,-0.17))+t*0.75));
    h += 0.30*crest(sin(dot(p,vec2( 0.23, 0.06))+t*1.35));
    return h;
}
float oceanHigh(vec2 p){
    float h=oceanLow(p);
    h += (fbm(p*0.35+vec2(0.0,time*0.18))-0.5)*0.75;
    h += (fbm(p*0.90-vec2(time*0.16,0.0))-0.5)*0.30;
    h += (fbm(p*2.10+vec2(time*0.25,0.0))-0.5)*0.12;
    return h;
}

/* ---------- sdf ---------- */
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.0))+min(max(q.x,max(q.y,q.z)),0.0); }
float sdCappedCone(vec3 p, float h, float r1, float r2){
    vec2 q=vec2(length(p.xz),p.y);
    vec2 k1=vec2(r2,h), k2=vec2(r2-r1,2.0*h);
    vec2 ca=vec2(q.x-min(q.x,(q.y<0.0)?r1:r2),abs(q.y)-h);
    vec2 cb=q-k1+k2*clamp(dot(k1-q,k2)/dot(k2,k2),0.0,1.0);
    float s=(cb.x<0.0&&ca.y<0.0)?-1.0:1.0;
    return s*sqrt(min(dot(ca,ca),dot(cb,cb)));
}
float towerSDF(vec3 p){
    vec2 cid=floor(p.xz/CELL);
    vec2 local=mod(p.xz,CELL)-0.5*CELL;
    vec3 q=vec3(local.x,p.y,local.y);
    float r0=hash21(cid), r1=hash21(cid+5.7);
    float halfW=0.85+r1*0.75;
    float botY=-9.0, topY, spireH;
    if(r0<0.18){ topY=-5.0; spireH=0.0; }
    else       { topY=1.0+r0*15.0; spireH=2.0+r1*5.5; }
    float cy=0.5*(botY+topY), halfH=0.5*(topY-botY);
    float s1=sdBox(q-vec3(0.0,cy,0.0),vec3(halfW,      halfH,halfW*0.55));
    float s2=sdBox(q-vec3(0.0,cy,0.0),vec3(halfW*0.55, halfH,halfW));
    float d=min(s1,s2);
    if(spireH>0.0){
        d=min(d,sdCappedCone(q-vec3(0.0,topY+spireH*0.5,0.0),spireH*0.5,halfW*1.0,0.04));
        float pin=1.0+r1*1.6;                                   // 4 corner pinnacles (abs-mirrored)
        vec3 qc=vec3(abs(q.x)-halfW*0.72, q.y-(topY+pin*0.5), abs(q.z)-halfW*0.72);
        d=min(d,sdCappedCone(qc,pin*0.5,0.16,0.02));
    }
    return d;
}
vec3 calcNormal(vec3 p){
    vec2 e=vec2(0.01,0.0);
    return normalize(vec3(towerSDF(p+e.xyy)-towerSDF(p-e.xyy),
                          towerSDF(p+e.yxy)-towerSDF(p-e.yxy),
                          towerSDF(p+e.yyx)-towerSDF(p-e.yyx)));
}
vec3 waterNormal(vec3 p){
    float e=0.10, h=oceanHigh(p.xz);
    return normalize(vec3(h-oceanHigh(p.xz+vec2(e,0.0)), e, h-oceanHigh(p.xz+vec2(0.0,e))));
}

/* ---------- gothic window: pointed (equilateral) arch + tracery + glow ---------- */
vec3 windowField(vec2 f){                 // f in [-0.5,0.5]; returns (pane, glow, glassArea)
    float halfW=0.30, bottom=-0.42, sh=0.02, A=0.38, e=0.012;
    float c=(A*A-halfW*halfW)/(2.0*halfW), R=halfW+c;
    float rx=smoothstep(halfW,halfW-e,abs(f.x));
    float ry=smoothstep(bottom-e,bottom,f.y)*smoothstep(sh,sh-e,f.y);
    float rect=rx*ry;
    float dl=(f.x+c)*(f.x+c)+(f.y-sh)*(f.y-sh);
    float dr=(f.x-c)*(f.x-c)+(f.y-sh)*(f.y-sh);
    float arch=smoothstep(R*R,R*R-0.02,max(dl,dr))*smoothstep(sh-e,sh,f.y);
    float glassA=clamp(max(rect,arch),0.0,1.0);
    float mull=smoothstep(0.018,0.030,abs(f.x));                // mullion
    float tran=smoothstep(0.016,0.028,abs(f.y-(sh-0.18)));      // transom
    float pane=glassA*min(mull,tran);
    float gr=length(vec2(f.x/0.34,f.y/0.42));
    return vec3(pane, exp(-gr*gr*1.3), glassA);
}

/* ---------- storm: full-scene flash + forked bolt event ---------- */
vec3 stormStrike(){          // (flashIntensity, boltX, boltLife)
    float t=time, flash=0.0, bx=0.0, blife=0.0;
    for(int i=0;i<3;i++){
        float fi=float(i), sp=0.31+fi*0.11, ph=t*sp+fi*7.0, seg=floor(ph);
        if(hash11(seg+fi*23.1)>0.80){
            float fr=fract(ph);
            float env=exp(-fr*12.0)+0.5*exp(-abs(fr-0.08)*20.0)+0.25*exp(-abs(fr-0.16)*18.0);
            env*=0.6+0.4*hash11(seg*1.7+fi);
            flash+=env;
            if(env>blife){ blife=env; bx=(hash11(seg*3.3+fi*5.0)*2.0-1.0)*0.9; }
        }
    }
    return vec3(clamp(flash,0.0,1.5),bx,clamp(blife,0.0,1.0));
}

/* ---------- sky ---------- */
vec3 skyColor(vec3 rd, vec3 strike){
    float fl=strike.x, y=clamp(rd.y,-0.3,1.0);
    vec3 col=mix(vec3(0.090,0.100,0.130),vec3(0.020,0.030,0.050),smoothstep(0.0,0.65,y));
    vec2 sp=rd.xz/(abs(rd.y)+0.20);
    float c1=fbm(sp*0.6+vec2(time*0.015,time*0.006));
    float c2=fbm(sp*1.4-vec2(time*0.010,0.0));
    float clouds=smoothstep(0.45,1.05,c1*0.7+c2*0.5);
    col=mix(col,mix(vec3(0.045,0.055,0.075),vec3(0.120,0.130,0.160),c2),clouds*(1.0-smoothstep(0.0,0.55,y)));
    float md=pow(clamp(dot(rd,normalize(vec3(0.30,0.55,0.60))),0.0,1.0),60.0);
    col+=vec3(0.20,0.22,0.28)*md*(1.0-clouds*0.8);
    col+=fl*mix(vec3(0.35,0.42,0.65),vec3(0.65,0.70,0.95),clouds)
            *(0.30+0.70*clouds)*(0.40+0.60*(1.0-smoothstep(0.0,0.70,y)));
    col+=vec3(0.090,0.100,0.130)*pow(1.0-clamp(abs(rd.y)/0.40,0.0,1.0),3.0)*0.40;
    return col;
}

/* ---------- stone ---------- */
vec3 stoneAlbedo(vec3 p, vec3 n){
    vec3 base=vec3(0.115,0.125,0.140);
    base*=mix(vec3(0.88,0.92,1.0),vec3(1.08,1.0,0.88),hash21(floor(p.xz/CELL)+2.3));
    vec2 suv=(abs(n.x)>abs(n.z))?vec2(p.z,p.y):vec2(p.x,p.y);
    base*=1.0-0.45*(1.0-smoothstep(0.0,0.16,abs(fract(suv.x*2.2+0.5)-0.5)));   // colonettes
    base*=1.0-0.28*(1.0-smoothstep(0.0,0.10,abs(fract(p.y*0.45)-0.5)));        // string courses
    base*=0.72+0.5*fbm(p.xz*0.6+p.y*0.25);                                     // grime
    base*=0.85+0.3*noise(suv*6.0);                                            // fine grain
    return base;
}
vec3 shadeStone(vec3 p, vec3 rd, vec3 strike){
    float flash=strike.x;
    vec3 n=calcNormal(p), alb=stoneAlbedo(p,n);
    float rel=p.y-oceanLow(p.xz);
    float wet=smoothstep(1.6,-0.3,rel);
    float algae=smoothstep(2.4,-0.6,rel)*smoothstep(-1.8,0.4,rel)*(0.5+0.5*fbm(p.xz*1.6+p.y*0.5));
    alb=mix(alb,vec3(0.05,0.11,0.06),clamp(algae*0.7,0.0,1.0));
    alb*=mix(1.0,0.55,wet);
    float dif=clamp(dot(n,SUN),0.0,1.0), sky=clamp(0.5+0.5*n.y,0.0,1.0);
    vec3 col=alb*0.16 + alb*sky*vec3(0.16,0.20,0.28) + alb*dif*vec3(0.5,0.5,0.55);
    float fres=pow(1.0-clamp(dot(n,-rd),0.0,1.0),4.0);
    col+=fres*vec3(0.12,0.15,0.20)*(0.5+0.5*wet);
    float sp=pow(clamp(dot(n,normalize(SUN-rd)),0.0,1.0),mix(30.0,120.0,wet));
    col+=sp*mix(0.15,0.9,wet)*vec3(0.55,0.62,0.72);
    col+=flash*alb*vec3(0.6,0.7,1.0)*(0.3+0.7*dif+0.5*fres);
    // windows
    float faceMask=smoothstep(0.55,0.22,abs(n.y));
    vec2 suv=(abs(n.x)>abs(n.z))?vec2(p.z,p.y):vec2(p.x,p.y);
    vec2 sc=suv/vec2(1.15,1.55), cell=floor(sc), f=fract(sc)-0.5;
    vec2 axisSeed=(abs(n.x)>abs(n.z))?vec2(11.0,3.0):vec2(2.0,17.0);
    vec2 cidp=floor(p.xz/CELL);
    vec3 win=windowField(f);
    float lsel=hash21(cell+cidp*3.7+axisSeed);
    float lit=step(WIN_LIT,lsel);
    vec3 wcol=vec3(1.0,0.60,0.26);
    float v1=hash21(cell+cidp*7.1+axisSeed);
    if(v1>0.90) wcol=vec3(0.45,0.80,1.0); else if(v1>0.82) wcol=vec3(0.5,1.0,0.62);
    float flick=0.78+0.18*sin(time*(2.5+lsel*5.0)+lsel*60.0)+0.06*sin(time*19.0+lsel*200.0);
    float gate=faceMask*smoothstep(-1.0,1.6,p.y)*(1.0-wet*0.7);
    col=mix(col,col*0.30,win.z*gate*(1.0-lit));
    col+=win.z*gate*(1.0-lit)*vec3(0.02,0.03,0.05);
    float e=gate*lit*flick;
    col+=win.x*e*wcol*2.4 + win.y*e*wcol*0.65;
    return col;
}

/* ---------- marchers ---------- */
float marchCity(vec3 ro, vec3 rd){
    float t=0.05;
    for(int i=0;i<CITY_STEPS;i++){ float d=towerSDF(ro+rd*t); if(d<0.002*t) return t; t+=clamp(d,0.02,2.0); if(t>FAR) break; }
    return -1.0;
}
float marchCityRefl(vec3 ro, vec3 rd){
    float t=0.1;
    for(int i=0;i<REFL_STEPS;i++){ float d=towerSDF(ro+rd*t); if(d<0.01*t) return t; t+=clamp(d,0.05,3.0); if(t>80.0) break; }
    return -1.0;
}
float marchWater(vec3 ro, vec3 rd){
    float t=0.05,lastT=t;
    for(int i=0;i<WATER_STEPS;i++){
        vec3 p=ro+rd*t; float h=oceanLow(p.xz);
        if(p.y-h<0.0){
            float a=lastT,b=t;
            for(int j=0;j<6;j++){ float m=0.5*(a+b); vec3 pm=ro+rd*m; if(pm.y-oceanLow(pm.xz)<0.0) b=m; else a=m; }
            return 0.5*(a+b);
        }
        lastT=t; t+=max(0.12,(p.y-h)*0.5); if(t>FAR) break;
    }
    return -1.0;
}

/* ---------- water ---------- */
vec3 shadeWater(vec3 p, vec3 rd, vec3 strike){
    float flash=strike.x;
    vec3 n=waterNormal(p), rfl=reflect(rd,n); rfl.y=max(rfl.y,0.02);
    vec3 rcol; float tr=marchCityRefl(p+n*0.05,rfl);
    if(tr>0.0) rcol=mix(shadeStone(p+rfl*tr,rfl,strike),skyColor(rfl,strike),1.0-exp(-tr*0.06));
    else       rcol=skyColor(rfl,strike);
    float crestH=oceanHigh(p.xz);
    vec3 tcol=vec3(0.012,0.030,0.040)+vec3(0.02,0.10,0.10)*smoothstep(0.4,1.6,crestH); // murk + crest glow
    float fres=0.02+0.98*pow(1.0-clamp(dot(n,-rd),0.0,1.0),5.0);
    vec3 col=mix(tcol,rcol,fres);
    float fn=fbm(p.xz*1.3+time*0.25), fn2=fbm(p.xz*3.0-time*0.4);
    float crestFoam=smoothstep(1.2,2.2,crestH)*smoothstep(0.35,0.85,fn);
    float streak=smoothstep(0.6,0.95,fn2)*smoothstep(0.8,1.6,crestH)*0.5;
    float baseFoam=(1.0-smoothstep(0.0,1.0,towerSDF(vec3(p.x,0.0,p.z))))*(0.5+0.5*fn)*0.9;
    float foam=clamp(max(max(crestFoam,streak),baseFoam),0.0,1.0)*(0.6+0.4*fn2);
    col=mix(col,vec3(0.78,0.82,0.85),foam);
    float spe=pow(clamp(dot(n,normalize(SUN-rd)),0.0,1.0),220.0);
    col+=spe*(0.4+3.0*flash)*vec3(0.8,0.85,1.0);
    col+=flash*fres*vec3(0.3,0.4,0.6);
    return col;
}

/* ---------- volumetrics: sweeping beacon + rain + lightning haze ---------- */
vec3 volumetrics(vec3 ro, vec3 rd, float tmax, vec3 strike){
    float vmax=min(tmax,90.0), dt=vmax/float(VOL_STEPS);
    float t=dt*(0.5+0.5*hash21(gl_FragCoord.xy));
    float ang=time*BEAM_SPEED;
    vec3 bdir=normalize(vec3(cos(ang),-0.16,sin(ang)));
    vec3 bpos=vec3(7.0,23.0,ro.z+34.0), acc=vec3(0.0);
    for(int i=0;i<VOL_STEPS;i++){
        if(t>vmax) break;
        vec3 q=ro+rd*t;
        float rfog=0.010+0.030*exp(-max(q.y+2.0,0.0)*0.10);
        vec3 toq=q-bpos; float along=dot(toq,bdir);
        if(along>0.5){
            vec3 perp=toq-along*bdir;
            float beam=exp(-dot(perp,perp)/(0.6+along*along*0.012))*exp(-along*0.018);
            beam*=0.5+0.9*fbm(q.xz*0.6+q.y*0.4+vec2(0.0,time*1.6));
            beam*=smoothstep(-2.0,16.0,q.y);
            acc+=beam*vec3(1.0,0.92,0.72)*BEAM_BRIGHT*dt;
        }
        acc+=strike.x*rfog*vec3(0.45,0.55,0.80)*0.5*dt;
        acc+=rfog*vec3(0.05,0.06,0.08)*0.3*dt;
        t+=dt;
    }
    return acc;
}

/* ---------- rain / bolt / tonemap ---------- */
float rainLayer(vec2 uv, float sc, float sp){
    uv*=sc; uv.x+=uv.y*0.25; uv.y+=time*sp; uv.x+=floor(uv.y);
    vec2 f=fract(uv);
    return (1.0-smoothstep(0.0,0.06,abs(f.x-0.5)))*smoothstep(0.0,0.2,f.y)*(1.0-smoothstep(0.55,1.0,f.y))*step(0.72,hash21(floor(uv)));
}
float boltGlow(vec2 uv, vec3 strike){
    float life=strike.z; if(life<0.02) return 0.0;
    float bx=strike.y, seedA=bx*7.0+3.1;
    float jit=(fbm(vec2(uv.y*3.5+seedA,seedA))-0.5)*0.6
            +(fbm(vec2(uv.y*11.0+seedA*2.0,seedA*0.7))-0.5)*0.22
            +(fbm(vec2(uv.y*26.0+seedA,seedA*1.3))-0.5)*0.08;
    float xp=bx+jit;
    float g=(0.010/(abs(uv.x-xp)+0.010))*smoothstep(-0.9,0.6,uv.y);
    if(uv.y<0.1){
        float jit2=(fbm(vec2(uv.y*9.0+seedA*3.0,seedA*4.0))-0.5)*0.5;
        g+=(0.006/(abs(uv.x-(xp+(0.1-uv.y)*1.2+jit2))+0.006))*0.6;     // fork
    }
    return g*life*1.4;
}
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0.0,1.0); }

void main(){
    vec2 uv=(gl_FragCoord.xy*2.0-resolution.xy)/resolution.y;
    vec3 strike=stormStrike();
    float ct=time;

    vec3 ro=vec3(0.7*sin(ct*0.25),4.6,ct*3.0);
    ro.y+=oceanLow(ro.xz)*0.30+sin(ct*0.8)*0.18;
    float pitch=-0.9+0.6*sin(ct*0.12);
    vec3 ta=ro+vec3(0.6*sin(ct*0.16),pitch,4.0);
    vec3 f=normalize(ta-ro), r=normalize(cross(vec3(0,1,0),f)), u=cross(f,r);
    float roll=sin(ct*0.45)*0.05+sin(ct*0.21)*0.025;
    vec3 rr=r*cos(roll)+u*sin(roll), uu=u*cos(roll)-r*sin(roll);
    vec3 rd=normalize(uv.x*rr+uv.y*uu+1.25*f);

    float tC=marchCity(ro,rd);
    float tW=(rd.y<0.0)?marchWater(ro,rd):-1.0;

    vec3 col; float dist;
    if(tC>0.0 && (tW<0.0||tC<tW)){ col=shadeStone(ro+rd*tC,rd,strike); dist=tC; }
    else if(tW>0.0)              { col=shadeWater(ro+rd*tW,rd,strike); dist=tW; }
    else                         { col=skyColor(rd,strike);            dist=FAR; }

    col=mix(col,skyColor(rd,strike),1.0-exp(-dist*0.016));            // fog
    col+=volumetrics(ro,rd,dist,strike);                             // beam + rain + haze
    col+=(rainLayer(uv,14.0,16.0)*0.8+rainLayer(uv*1.7,22.0,22.0)*0.5)*0.03*vec3(0.8,0.85,0.95);
    col+=boltGlow(uv,strike)*vec3(0.75,0.82,1.0);                    // visible bolt
    col*=1.04;
    col=mix(col,col*vec3(0.9,1.0,1.04),0.3);                         // cool the shadows
    col*=1.0-0.18*dot(uv,uv);                                        // vignette
    col=aces(col);
    col=pow(col,vec3(0.95));
    gl_FragColor=vec4(col,1.0);
}

**Quelle:** [X - Ethan Mollick](http://nitter.perennialte.ch/emollick/status/2060043661920919820#m)  
**Autor:** Ethan Mollick  
**Veröffentlicht:** Thu, 28 May 2026 17:00:57 GMT  
**Gescannt:** 2026-05-28

---

## Inhalt

This is hard! It involves raymarching repeating gothic architecture (instancing towers across an infinite grid with gothic silhouettes and windows), a displaced ocean surface with believable wave motion, and stormy atmospheric lighting/fog to tie it together... and doing this all with no textures or external assets, just math.

Here is the full code:

/*  D R O W N E D   C A T H E D R A L   C I T Y   ·  mk2   —   (classic)  */
precision highp float;
uniform vec2 resolution;
uniform vec2 mouse;
uniform float time;

#define CITY_STEPS  90
#define WATER_STEPS 60
#define REFL_STEPS  20
#define VOL_STEPS   18
#define FAR  200.0
#define CELL 8.0
#define CREST_K     2.2     // wave crest sharpness (1 = round sine, higher = choppier)
#define WIN_LIT     0.46    // fraction of windows lit (lower = more lit)
#define BEAM_BRIGHT 0.07    // lighthouse beam intensity
#define BEAM_SPEED  0.50    // beam rotation speed
const vec3 SUN = vec3(-0.548, 0.685, -0.480);

/* ---------- hash / noise ---------- */
float hash21(vec2 p){ p=fract(p*vec2(123.34,345.45)); p+=dot(p,p+34.345); return fract(p.x*p.y); }
float hash11(float n){ return fract(sin(n)*43758.5453123); }
float noise(vec2 p){
    vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
    return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),
               mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x),f.y);
}
float fbm(vec2 p){
    float v=0.0,a=0.5; mat2 m=mat2(1.6,1.2,-1.2,1.6);
    for(int i=0;i<4;i++){ v+=a*noise(p); p=m*p; a*=0.5; } return v;
}

/* ---------- ocean ---------- */
float crest(float s){ float u=0.5+0.5*s; u=pow(u,CREST_K); return u*2.0-1.0; }
float oceanLow(vec2 p){
    float t=time, h=0.0;
    h += 0.95*crest(sin(dot(p,vec2( 0.16, 0.11))+t*1.10));
    h += 0.70*crest(sin(dot(p,vec2(-0.12, 0.21))-t*0.90));
    h += 0.50*crest(sin(dot(p,vec2( 0.09,-0.17))+t*0.75));
    h += 0.30*crest(sin(dot(p,vec2( 0.23, 0.06))+t*1.35));
    return h;
}
float oceanHigh(vec2 p){
    float h=oceanLow(p);
    h += (fbm(p*0.35+vec2(0.0,time*0.18))-0.5)*0.75;
    h += (fbm(p*0.90-vec2(time*0.16,0.0))-0.5)*0.30;
    h += (fbm(p*2.10+vec2(time*0.25,0.0))-0.5)*0.12;
    return h;
}

/* ---------- sdf ---------- */
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.0))+min(max(q.x,max(q.y,q.z)),0.0); }
float sdCappedCone(vec3 p, float h, float r1, float r2){
    vec2 q=vec2(length(p.xz),p.y);
    vec2 k1=vec2(r2,h), k2=vec2(r2-r1,2.0*h);
    vec2 ca=vec2(q.x-min(q.x,(q.y<0.0)?r1:r2),abs(q.y)-h);
    vec2 cb=q-k1+k2*clamp(dot(k1-q,k2)/dot(k2,k2),0.0,1.0);
    float s=(cb.x<0.0&&ca.y<0.0)?-1.0:1.0;
    return s*sqrt(min(dot(ca,ca),dot(cb,cb)));
}
float towerSDF(vec3 p){
    vec2 cid=floor(p.xz/CELL);
    vec2 local=mod(p.xz,CELL)-0.5*CELL;
    vec3 q=vec3(local.x,p.y,local.y);
    float r0=hash21(cid), r1=hash21(cid+5.7);
    float halfW=0.85+r1*0.75;
    float botY=-9.0, topY, spireH;
    if(r0<0.18){ topY=-5.0; spireH=0.0; }
    else       { topY=1.0+r0*15.0; spireH=2.0+r1*5.5; }
    float cy=0.5*(botY+topY), halfH=0.5*(topY-botY);
    float s1=sdBox(q-vec3(0.0,cy,0.0),vec3(halfW,      halfH,halfW*0.55));
    float s2=sdBox(q-vec3(0.0,cy,0.0),vec3(halfW*0.55, halfH,halfW));
    float d=min(s1,s2);
    if(spireH>0.0){
        d=min(d,sdCappedCone(q-vec3(0.0,topY+spireH*0.5,0.0),spireH*0.5,halfW*1.0,0.04));
        float pin=1.0+r1*1.6;                                   // 4 corner pinnacles (abs-mirrored)
        vec3 qc=vec3(abs(q.x)-halfW*0.72, q.y-(topY+pin*0.5), abs(q.z)-halfW*0.72);
        d=min(d,sdCappedCone(qc,pin*0.5,0.16,0.02));
    }
    return d;
}
vec3 calcNormal(vec3 p){
    vec2 e=vec2(0.01,0.0);
    return normalize(vec3(towerSDF(p+e.xyy)-towerSDF(p-e.xyy),
                          towerSDF(p+e.yxy)-towerSDF(p-e.yxy),
                          towerSDF(p+e.yyx)-towerSDF(p-e.yyx)));
}
vec3 waterNormal(vec3 p){
    float e=0.10, h=oceanHigh(p.xz);
    return normalize(vec3(h-oceanHigh(p.xz+vec2(e,0.0)), e, h-oceanHigh(p.xz+vec2(0.0,e))));
}

/* ---------- gothic window: pointed (equilateral) arch + tracery + glow ---------- */
vec3 windowField(vec2 f){                 // f in [-0.5,0.5]; returns (pane, glow, glassArea)
    float halfW=0.30, bottom=-0.42, sh=0.02, A=0.38, e=0.012;
    float c=(A*A-halfW*halfW)/(2.0*halfW), R=halfW+c;
    float rx=smoothstep(halfW,halfW-e,abs(f.x));
    float ry=smoothstep(bottom-e,bottom,f.y)*smoothstep(sh,sh-e,f.y);
    float rect=rx*ry;
    float dl=(f.x+c)*(f.x+c)+(f.y-sh)*(f.y-sh);
    float dr=(f.x-c)*(f.x-c)+(f.y-sh)*(f.y-sh);
    float arch=smoothstep(R*R,R*R-0.02,max(dl,dr))*smoothstep(sh-e,sh,f.y);
    float glassA=clamp(max(rect,arch),0.0,1.0);
    float mull=smoothstep(0.018,0.030,abs(f.x));                // mullion
    float tran=smoothstep(0.016,0.028,abs(f.y-(sh-0.18)));      // transom
    float pane=glassA*min(mull,tran);
    float gr=length(vec2(f.x/0.34,f.y/0.42));
    return vec3(pane, exp(-gr*gr*1.3), glassA);
}

/* ---------- storm: full-scene flash + forked bolt event ---------- */
vec3 stormStrike(){          // (flashIntensity, boltX, boltLife)
    float t=time, flash=0.0, bx=0.0, blife=0.0;
    for(int i=0;i<3;i++){
        float fi=float(i), sp=0.31+fi*0.11, ph=t*sp+fi*7.0, seg=floor(ph);
        if(hash11(seg+fi*23.1)>0.80){
            float fr=fract(ph);
            float env=exp(-fr*12.0)+0.5*exp(-abs(fr-0.08)*20.0)+0.25*exp(-abs(fr-0.16)*18.0);
            env*=0.6+0.4*hash11(seg*1.7+fi);
            flash+=env;
            if(env>blife){ blife=env; bx=(hash11(seg*3.3+fi*5.0)*2.0-1.0)*0.9; }
        }
    }
    return vec3(clamp(flash,0.0,1.5),bx,clamp(blife,0.0,1.0));
}

/* ---------- sky ---------- */
vec3 skyColor(vec3 rd, vec3 strike){
    float fl=strike.x, y=clamp(rd.y,-0.3,1.0);
    vec3 col=mix(vec3(0.090,0.100,0.130),vec3(0.020,0.030,0.050),smoothstep(0.0,0.65,y));
    vec2 sp=rd.xz/(abs(rd.y)+0.20);
    float c1=fbm(sp*0.6+vec2(time*0.015,time*0.006));
    float c2=fbm(sp*1.4-vec2(time*0.010,0.0));
    float clouds=smoothstep(0.45,1.05,c1*0.7+c2*0.5);
    col=mix(col,mix(vec3(0.045,0.055,0.075),vec3(0.120,0.130,0.160),c2),clouds*(1.0-smoothstep(0.0,0.55,y)));
    float md=pow(clamp(dot(rd,normalize(vec3(0.30,0.55,0.60))),0.0,1.0),60.0);
    col+=vec3(0.20,0.22,0.28)*md*(1.0-clouds*0.8);
    col+=fl*mix(vec3(0.35,0.42,0.65),vec3(0.65,0.70,0.95),clouds)
            *(0.30+0.70*clouds)*(0.40+0.60*(1.0-smoothstep(0.0,0.70,y)));
    col+=vec3(0.090,0.100,0.130)*pow(1.0-clamp(abs(rd.y)/0.40,0.0,1.0),3.0)*0.40;
    return col;
}

/* ---------- stone ---------- */
vec3 stoneAlbedo(vec3 p, vec3 n){
    vec3 base=vec3(0.115,0.125,0.140);
    base*=mix(vec3(0.88,0.92,1.0),vec3(1.08,1.0,0.88),hash21(floor(p.xz/CELL)+2.3));
    vec2 suv=(abs(n.x)>abs(n.z))?vec2(p.z,p.y):vec2(p.x,p.y);
    base*=1.0-0.45*(1.0-smoothstep(0.0,0.16,abs(fract(suv.x*2.2+0.5)-0.5)));   // colonettes
    base*=1.0-0.28*(1.0-smoothstep(0.0,0.10,abs(fract(p.y*0.45)-0.5)));        // string courses
    base*=0.72+0.5*fbm(p.xz*0.6+p.y*0.25);                                     // grime
    base*=0.85+0.3*noise(suv*6.0);                                            // fine grain
    return base;
}
vec3 shadeStone(vec3 p, vec3 rd, vec3 strike){
    float flash=strike.x;
    vec3 n=calcNormal(p), alb=stoneAlbedo(p,n);
    float rel=p.y-oceanLow(p.xz);
    float wet=smoothstep(1.6,-0.3,rel);
    float algae=smoothstep(2.4,-0.6,rel)*smoothstep(-1.8,0.4,rel)*(0.5+0.5*fbm(p.xz*1.6+p.y*0.5));
    alb=mix(alb,vec3(0.05,0.11,0.06),clamp(algae*0.7,0.0,1.0));
    alb*=mix(1.0,0.55,wet);
    float dif=clamp(dot(n,SUN),0.0,1.0), sky=clamp(0.5+0.5*n.y,0.0,1.0);
    vec3 col=alb*0.16 + alb*sky*vec3(0.16,0.20,0.28) + alb*dif*vec3(0.5,0.5,0.55);
    float fres=pow(1.0-clamp(dot(n,-rd),0.0,1.0),4.0);
    col+=fres*vec3(0.12,0.15,0.20)*(0.5+0.5*wet);
    float sp=pow(clamp(dot(n,normalize(SUN-rd)),0.0,1.0),mix(30.0,120.0,wet));
    col+=sp*mix(0.15,0.9,wet)*vec3(0.55,0.62,0.72);
    col+=flash*alb*vec3(0.6,0.7,1.0)*(0.3+0.7*dif+0.5*fres);
    // windows
    float faceMask=smoothstep(0.55,0.22,abs(n.y));
    vec2 suv=(abs(n.x)>abs(n.z))?vec2(p.z,p.y):vec2(p.x,p.y);
    vec2 sc=suv/vec2(1.15,1.55), cell=floor(sc), f=fract(sc)-0.5;
    vec2 axisSeed=(abs(n.x)>abs(n.z))?vec2(11.0,3.0):vec2(2.0,17.0);
    vec2 cidp=floor(p.xz/CELL);
    vec3 win=windowField(f);
    float lsel=hash21(cell+cidp*3.7+axisSeed);
    float lit=step(WIN_LIT,lsel);
    vec3 wcol=vec3(1.0,0.60,0.26);
    float v1=hash21(cell+cidp*7.1+axisSeed);
    if(v1>0.90) wcol=vec3(0.45,0.80,1.0); else if(v1>0.82) wcol=vec3(0.5,1.0,0.62);
    float flick=0.78+0.18*sin(time*(2.5+lsel*5.0)+lsel*60.0)+0.06*sin(time*19.0+lsel*200.0);
    float gate=faceMask*smoothstep(-1.0,1.6,p.y)*(1.0-wet*0.7);
    col=mix(col,col*0.30,win.z*gate*(1.0-lit));
    col+=win.z*gate*(1.0-lit)*vec3(0.02,0.03,0.05);
    float e=gate*lit*flick;
    col+=win.x*e*wcol*2.4 + win.y*e*wcol*0.65;
    return col;
}

/* ---------- marchers ---------- */
float marchCity(vec3 ro, vec3 rd){
    float t=0.05;
    for(int i=0;i<CITY_STEPS;i++){ float d=towerSDF(ro+rd*t); if(d<0.002*t) return t; t+=clamp(d,0.02,2.0); if(t>FAR) break; }
    return -1.0;
}
float marchCityRefl(vec3 ro, vec3 rd){
    float t=0.1;
    for(int i=0;i<REFL_STEPS;i++){ float d=towerSDF(ro+rd*t); if(d<0.01*t) return t; t+=clamp(d,0.05,3.0); if(t>80.0) break; }
    return -1.0;
}
float marchWater(vec3 ro, vec3 rd){
    float t=0.05,lastT=t;
    for(int i=0;i<WATER_STEPS;i++){
        vec3 p=ro+rd*t; float h=oceanLow(p.xz);
        if(p.y-h<0.0){
            float a=lastT,b=t;
            for(int j=0;j<6;j++){ float m=0.5*(a+b); vec3 pm=ro+rd*m; if(pm.y-oceanLow(pm.xz)<0.0) b=m; else a=m; }
            return 0.5*(a+b);
        }
        lastT=t; t+=max(0.12,(p.y-h)*0.5); if(t>FAR) break;
    }
    return -1.0;
}

/* ---------- water ---------- */
vec3 shadeWater(vec3 p, vec3 rd, vec3 strike){
    float flash=strike.x;
    vec3 n=waterNormal(p), rfl=reflect(rd,n); rfl.y=max(rfl.y,0.02);
    vec3 rcol; float tr=marchCityRefl(p+n*0.05,rfl);
    if(tr>0.0) rcol=mix(shadeStone(p+rfl*tr,rfl,strike),skyColor(rfl,strike),1.0-exp(-tr*0.06));
    else       rcol=skyColor(rfl,strike);
    float crestH=oceanHigh(p.xz);
    vec3 tcol=vec3(0.012,0.030,0.040)+vec3(0.02,0.10,0.10)*smoothstep(0.4,1.6,crestH); // murk + crest glow
    float fres=0.02+0.98*pow(1.0-clamp(dot(n,-rd),0.0,1.0),5.0);
    vec3 col=mix(tcol,rcol,fres);
    float fn=fbm(p.xz*1.3+time*0.25), fn2=fbm(p.xz*3.0-time*0.4);
    float crestFoam=smoothstep(1.2,2.2,crestH)*smoothstep(0.35,0.85,fn);
    float streak=smoothstep(0.6,0.95,fn2)*smoothstep(0.8,1.6,crestH)*0.5;
    float baseFoam=(1.0-smoothstep(0.0,1.0,towerSDF(vec3(p.x,0.0,p.z))))*(0.5+0.5*fn)*0.9;
    float foam=clamp(max(max(crestFoam,streak),baseFoam),0.0,1.0)*(0.6+0.4*fn2);
    col=mix(col,vec3(0.78,0.82,0.85),foam);
    float spe=pow(clamp(dot(n,normalize(SUN-rd)),0.0,1.0),220.0);
    col+=spe*(0.4+3.0*flash)*vec3(0.8,0.85,1.0);
    col+=flash*fres*vec3(0.3,0.4,0.6);
    return col;
}

/* ---------- volumetrics: sweeping beacon + rain + lightning haze ---------- */
vec3 volumetrics(vec3 ro, vec3 rd, float tmax, vec3 strike){
    float vmax=min(tmax,90.0), dt=vmax/float(VOL_STEPS);
    float t=dt*(0.5+0.5*hash21(gl_FragCoord.xy));
    float ang=time*BEAM_SPEED;
    vec3 bdir=normalize(vec3(cos(ang),-0.16,sin(ang)));
    vec3 bpos=vec3(7.0,23.0,ro.z+34.0), acc=vec3(0.0);
    for(int i=0;i<VOL_STEPS;i++){
        if(t>vmax) break;
        vec3 q=ro+rd*t;
        float rfog=0.010+0.030*exp(-max(q.y+2.0,0.0)*0.10);
        vec3 toq=q-bpos; float along=dot(toq,bdir);
        if(along>0.5){
            vec3 perp=toq-along*bdir;
            float beam=exp(-dot(perp,perp)/(0.6+along*along*0.012))*exp(-along*0.018);
            beam*=0.5+0.9*fbm(q.xz*0.6+q.y*0.4+vec2(0.0,time*1.6));
            beam*=smoothstep(-2.0,16.0,q.y);
            acc+=beam*vec3(1.0,0.92,0.72)*BEAM_BRIGHT*dt;
        }
        acc+=strike.x*rfog*vec3(0.45,0.55,0.80)*0.5*dt;
        acc+=rfog*vec3(0.05,0.06,0.08)*0.3*dt;
        t+=dt;
    }
    return acc;
}

/* ---------- rain / bolt / tonemap ---------- */
float rainLayer(vec2 uv, float sc, float sp){
    uv*=sc; uv.x+=uv.y*0.25; uv.y+=time*sp; uv.x+=floor(uv.y);
    vec2 f=fract(uv);
    return (1.0-smoothstep(0.0,0.06,abs(f.x-0.5)))*smoothstep(0.0,0.2,f.y)*(1.0-smoothstep(0.55,1.0,f.y))*step(0.72,hash21(floor(uv)));
}
float boltGlow(vec2 uv, vec3 strike){
    float life=strike.z; if(life<0.02) return 0.0;
    float bx=strike.y, seedA=bx*7.0+3.1;
    float jit=(fbm(vec2(uv.y*3.5+seedA,seedA))-0.5)*0.6
            +(fbm(vec2(uv.y*11.0+seedA*2.0,seedA*0.7))-0.5)*0.22
            +(fbm(vec2(uv.y*26.0+seedA,seedA*1.3))-0.5)*0.08;
    float xp=bx+jit;
    float g=(0.010/(abs(uv.x-xp)+0.010))*smoothstep(-0.9,0.6,uv.y);
    if(uv.y<0.1){
        float jit2=(fbm(vec2(uv.y*9.0+seedA*3.0,seedA*4.0))-0.5)*0.5;
        g+=(0.006/(abs(uv.x-(xp+(0.1-uv.y)*1.2+jit2))+0.006))*0.6;     // fork
    }
    return g*life*1.4;
}
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0.0,1.0); }

void main(){
    vec2 uv=(gl_FragCoord.xy*2.0-resolution.xy)/resolution.y;
    vec3 strike=stormStrike();
    float ct=time;

    vec3 ro=vec3(0.7*sin(ct*0.25),4.6,ct*3.0);
    ro.y+=oceanLow(ro.xz)*0.30+sin(ct*0.8)*0.18;
    float pitch=-0.9+0.6*sin(ct*0.12);
    vec3 ta=ro+vec3(0.6*sin(ct*0.16),pitch,4.0);
    vec3 f=normalize(ta-ro), r=normalize(cross(vec3(0,1,0),f)), u=cross(f,r);
    float roll=sin(ct*0.45)*0.05+sin(ct*0.21)*0.025;
    vec3 rr=r*cos(roll)+u*sin(roll), uu=u*cos(roll)-r*sin(roll);
    vec3 rd=normalize(uv.x*rr+uv.y*uu+1.25*f);

    float tC=marchCity(ro,rd);
    float tW=(rd.y<0.0)?marchWater(ro,rd):-1.0;

    vec3 col; float dist;
    if(tC>0.0 && (tW<0.0||tC<tW)){ col=shadeStone(ro+rd*tC,rd,strike); dist=tC; }
    else if(tW>0.0)              { col=shadeWater(ro+rd*tW,rd,strike); dist=tW; }
    else                         { col=skyColor(rd,strike);            dist=FAR; }

    col=mix(col,skyColor(rd,strike),1.0-exp(-dist*0.016));            // fog
    col+=volumetrics(ro,rd,dist,strike);                             // beam + rain + haze
    col+=(rainLayer(uv,14.0,16.0)*0.8+rainLayer(uv*1.7,22.0,22.0)*0.5)*0.03*vec3(0.8,0.85,0.95);
    col+=boltGlow(uv,strike)*vec3(0.75,0.82,1.0);                    // visible bolt
    col*=1.04;
    col=mix(col,col*vec3(0.9,1.0,1.04),0.3);                         // cool the shadows
    col*=1.0-0.18*dot(uv,uv);                                        // vignette
    col=aces(col);
    col=pow(col,vec3(0.95));
    gl_FragColor=vec4(col,1.0);
}

## Siehe auch
- [[40_Areas/ai-news-index|Ai News Index]]
- [[40_Areas/dev-news-index|Dev News Index]]
- [[_meta/index/MOC|Master of Ceremonies]]
