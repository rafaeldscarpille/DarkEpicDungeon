"""Adiciona o Capitão Scarpa (classe PIRATE, um Berserker pirata) ao bundle do jogo.

O projeto só tem o bundle compilado (assets/index-*.js), então cada mudança é uma
troca de texto que precisa casar exatamente uma vez. Se já foi aplicada, pula.

Uso:  python scripts/patch_pirate_class.py
"""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "assets", "index-D6qIWtA7-p209.js")
MIRROR = os.path.join(ROOT, "Projeto atualizado", "assets", "index-D6qIWtA7-p209.js")

s = open(BUNDLE, encoding="utf-8").read()
MARK = 'PIRATE:{id:"PIRATE"'
if MARK in s:
    print("já aplicado — nada a fazer")
    sys.exit(0)


def rep(old, new, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit(f"esperava {count} ocorrência(s), achei {n}: {old[:90]!r}")
    s = s.replace(old, new)


# ------------------------------------------------------------------ classe
PIRATE_DEF = (
    'PIRATE:{id:"PIRATE",name:"Berserker",texture:"player-pirate",'
    'tagline:"Capitão pirata e berserker: crava a âncora, solta o papagaio e desperta a ira do Kraken.",'
    'desc:["Sabre e âncora","Fúria crescente","Papagaio companheiro"],attackType:"melee",'
    'baseStats:{maxHp:8,damage:3,magicDamage:0,defense:1,speed:162,critChance:8,critMult:1.7,attackSpeed:1},'
    'levelBonus:{maxHp:1.9,damage:.7,defense:.25,speed:0,critChance:.4,magicDamage:0,maxResource:0},'
    'resource:{type:"fury",name:"Fúria",max:100,regen:-5,color:14702138},'
    'abilities:["FURIA_PIRATA","FRENZY","COMPANHEIRO_VOADOR"]},'
)
rep('abilities:["IAIJUTSU","KIAI","KAZE_GIRI"]},', 'abilities:["IAIJUTSU","KIAI","KAZE_GIRI"]},' + PIRATE_DEF)

# árvore de habilidades: Fúria Pirata primeiro, habilidades clássicas do Berserker no meio, Kraken no fim
rep('15:["KAISHAKU"]},',
    '15:["KAISHAKU"]},PIRATE:{1:["FURIA_PIRATA"],5:["FRENZY","COMPANHEIRO_VOADOR"],10:["DEMOLISHING_BLOW","BLOODLUST"],15:["IRA_KRAKEN"]},')

# habilidades novas (mesmo bloco onde o Xamã registra as dele)
ABILITIES = (
    'FURIA_PIRATA:{id:"FURIA_PIRATA",name:"Fúria Pirata",'
    'desc:"Salta e crava uma âncora gigante no chão: dano massivo em área e atordoa os inimigos próximos por 2s.",'
    'icon:"icon-demolish",type:"anchor-slam",damageType:"physical",cost:25,cooldown:8,damageMult:3,radius:90,'
    'stun:2,knockbackMult:.8,color:9080698,tint:9080698,sound:"sfx-warrior-heavy-strike"},'
    'COMPANHEIRO_VOADOR:{...Ye.EAGLE_COMPANION,id:"COMPANHEIRO_VOADOR",name:"Companheiro Voador",'
    'desc:"Solta o papagaio do capitão por 30s: ele voa pela sala e traz itens, poções e ouro para você.",'
    'cost:20,texture:"pirate-parrot",label:"Papagaio!",color:14692906},'
    'IRA_KRAKEN:{id:"IRA_KRAKEN",name:"Ira do Kraken",'
    'desc:"Fúria total por 10s: imune a controle (atordoamento, lentidão e empurrões), +50% de dano, '
    'e cada ataque invoca tentáculos fantasmagóricos que esmagam os inimigos.",'
    'icon:"icon-bloodlust",type:"kraken",cost:60,cooldown:30,duration:10,damageBonus:.5,tentacleMult:.9,'
    'tentacleRange:150,color:3002312,tint:10475744,sound:"sfx-warrior-whirlwind"},'
)
rep('Object.assign(Ye,{RAIZES_JUREMA:', 'Object.assign(Ye,{' + ABILITIES + 'RAIZES_JUREMA:')

# ------------------------------------------------------------------ atordoamento
rep('SLOW:{key:"SLOW",name:"Lentidão",color:10137804,speedMult:.7,maxDuration:4,text:"LENTO"}}',
    'SLOW:{key:"SLOW",name:"Lentidão",color:10137804,speedMult:.7,maxDuration:4,text:"LENTO"},'
    'STUN:{key:"STUN",name:"Atordoamento",color:16770650,speedMult:.01,maxDuration:3,text:"ATORDOADO"}}')
# Ira do Kraken: o jogador fica imune a qualquer status negativo
rep('apply(i,t,{duration:e=3,power:d=1}={}){const o=ai[t];if(!o||!i||i.dead)return;',
    'apply(i,t,{duration:e=3,power:d=1}={}){const o=ai[t];if(!o||!i||i.dead)return;'
    'if(i===this.scene.player&&this.scene.__krakenUntil>this.scene.time.now)return;')
# inimigo comum atordoado: para de pensar e de andar
rep('this.ai.update(i,t),this.knock.x!==0',
    '(this.statuses?.STUN?.t>0?this.setVelocity(0,0):this.ai.update(i,t)),this.knock.x!==0')
# chefe atordoado (o tempo já é cortado pela metade em chefes)
rep('this.state_){case"idle":this.setVelocity(0,0),t.dead||(this.state_="chase");break;',
    '(this.statuses?.STUN?.t>0&&this.state_==="chase"?"__stun":this.state_)){case"__stun":this.setVelocity(0,0);break;'
    'case"idle":this.setVelocity(0,0),t.dead||(this.state_="chase");break;')
# Kraken: sem empurrão ao levar dano
rep('this.scene.resource.gain(12),t&&(this.knock.x=t.x*this.data_.hitKnockback',
    'this.scene.resource.gain(12),t&&!(this.scene.__krakenUntil>this.scene.time.now)&&(this.knock.x=t.x*this.data_.hitKnockback')

# ------------------------------------------------------------------ execução das habilidades
rep('case"eagle":return this.execEagle(i);',
    'case"eagle":return this.execEagle(i);case"anchor-slam":return this.execAnchorSlam(i);case"kraken":return this.execKraken(i);')

METHODS = r'''execAnchorSlam(i){const S=this.scene,p=S.player,v=S.playerVisual,fd=this.facingDir(),R=i.radius,dir=fd.x<-.1?-1:fd.x>.1?1:(v?.lastSideSign??1),M=v?.mk2Layout?.map??{},pose=f=>{v&&(v.__poseF=f??null)},setHop=h=>{v&&(v.__hop=h)},T0=110,TUP=210,TSW=140,TIMP=T0+TUP+TSW;pose(M.guard??M.guardStart);S.effects.burstTinted(p.x,p.y+10,9076582,6);const hop={h:0};S.time.delayedCall(T0,()=>{pose(M.dash??M.dashA);S.tweens.add({targets:hop,h:28,duration:TUP,ease:"Quad.easeOut",onUpdate:()=>setHop(hop.h)})});S.time.delayedCall(T0+TUP,()=>{S.tweens.add({targets:hop,h:0,duration:TSW,ease:"Quad.easeIn",onUpdate:()=>setHop(hop.h)})});let anc=null,follow=null;if(S.textures.exists("pirate-anchor")){const r0=dir*Math.PI*.82,r1=dir*Math.PI*1.74,piv=()=>({x:p.x+dir*3,y:p.y-24-(v?.__hop||0)});anc=S.add.image(piv().x,piv().y,"pirate-anchor").setOrigin(.5,.07).setScale(.6).setRotation(r0).setAlpha(0);follow=S.time.addEvent({delay:16,loop:!0,callback:()=>{if(!anc?.active)return;const q=piv();anc.setPosition(q.x,q.y).setDepth(p.y+3)}});S.tweens.add({targets:anc,alpha:1,delay:T0,duration:110});S.time.delayedCall(T0+TUP,()=>{anc?.active&&(anc.__sw=S.tweens.add({targets:anc,rotation:r1,duration:TSW-8,ease:"Cubic.easeIn"}))})}S.time.delayedCall(TIMP,()=>{follow?.remove(),setHop(0);if(!S.scene.isActive()||!p.active||p.dead){anc?.destroy(),pose(null);return}pose(M.cast??M.hit);const cx=p.x+dir*26,cy=p.y+8,ax=p.x+dir*12,ay=p.y+6;anc&&(anc.__sw?.stop(),anc.setOrigin(.5,.93).setRotation(-dir*.32).setPosition(cx,cy+3).setDepth(cy+12));__pirateImpact(S,cx,cy,R);const{amount:am,crit:cr2}=this.rollDamage(i);for(const n of S.combat.getTargets())if(S.damageSystem.circleHit(ax,ay,R,n.x,n.y,(n.body?.width??16)/2)){const d=Math.hypot(n.x-ax,n.y-ay)||1;S.damageSystem.apply({target:n,amount:am,critical:cr2,type:i.damageType,dir:{x:(n.x-ax)/d,y:(n.y-ay)/d},knockbackMult:i.knockbackMult??1,status:{key:"STUN",duration:i.stun??2}}),n.dead||this.__stunStars(n)}S.time.delayedCall(260,()=>pose(M.guard??null)),S.time.delayedCall(440,()=>pose(null));anc&&S.tweens.add({targets:anc,alpha:0,y:anc.y+6,delay:1100,duration:500,onComplete:()=>anc.destroy()})})}__stunStars(n){const S=this.scene;if(n.__stars)return;const g=S.add.graphics();n.__stars=g;let t=0;const ev=S.time.addEvent({delay:16,loop:!0,callback:()=>{if(!n.active||n.dead||!(n.statuses?.STUN?.t>0)||!S.scene.isActive()){ev.remove(),g.destroy(),n.__stars=null;return}t+=.016;const hx=n.x,hy=n.y-(n.displayHeight??24)/2-5;g.clear().setDepth(n.y+60);for(let k=0;k<3;k++){const a=t*5+k*2.094,x=hx+Math.cos(a)*9,y=hy+Math.sin(a)*3,front=Math.sin(a)>0;g.fillStyle(16765514,front?1:.55).fillRect(x-1,y-2,2,4).fillRect(x-2,y-1,4,2),g.fillStyle(16777215,front?1:.5).fillRect(x-.5,y-.5,1,1)}}})}execKraken(i){const S=this.scene,p=S.player,v=S.playerVisual,ms=i.duration*1e3;S.__krakenEnd?.();S.__krakenUntil=S.time.now+ms;if(p.statuses)for(const k of Object.keys(p.statuses))delete p.statuses[k];const tot=S.stats.total;S.stats.addBuff("damage",Math.max(1,Math.round((tot.damage??1)*(i.damageBonus??.5))),i.duration);S.effects.floatText(p.x,p.y-36,"IRA DO KRAKEN!","#5ee0d0",12),S.cameraSys.shake(.008,320),S.effects.burstTinted(p.x,p.y,i.color,30),S.effects.shockwaveRing(p.x,p.y,64);const pool=S.add.ellipse(p.x,p.y+8,56,18,792617,.62),glow=S.add.image(p.x,p.y+6,"light").setBlendMode(j.BlendModes.ADD).setTint(i.color).setScale(.42,.2).setAlpha(.55),eye=S.add.image(p.x,p.y,"light").setBlendMode(j.BlendModes.ADD).setTint(9174015).setScale(.2,.26).setAlpha(0);let tt=0;const tick=S.time.addEvent({delay:16,loop:!0,callback:()=>{if(!p.active)return;tt+=16;const pu=Math.sin(S.time.now*.009);pool.setPosition(p.x,p.y+8).setDepth(p.y-3).setScale(1+pu*.06),glow.setPosition(p.x,p.y+6).setDepth(p.y-2).setAlpha(.42+pu*.14);const hy=v?.container?v.container.y-(v.__hop||0)-20:p.y-20,hx=p.x;eye.setPosition(hx,hy).setDepth(p.y-1).setAlpha(.3+Math.sin(S.time.now*.012)*.1);tt>=250&&(tt=0,v?.setTintAll?.(i.tint))}}),drops=S.time.addEvent({delay:95,loop:!0,callback:()=>{if(!p.active)return;const a=Math.random()*Math.PI*2,r=10+Math.random()*13,x=p.x+Math.cos(a)*r,y=p.y+6+Math.sin(a)*r*.4,d=S.add.rectangle(x,y,2,3,Math.random()<.5?2650538:6216400).setDepth(p.y+6).setAlpha(.9);S.tweens.add({targets:d,y:y-24-Math.random()*16,alpha:0,duration:620,onComplete:()=>d.destroy()})}});v?.setTintAll?.(i.tint),S.__krakenStrike=()=>this.krakenTentacle(i);const end=()=>{tick.remove(),drops.remove(),pool.destroy(),glow.destroy(),eye.destroy(),v?.clearTintAll?.(),S.__krakenStrike=null,S.__krakenEnd=null,S.__krakenUntil=0};S.__krakenEnd=end,S.time.delayedCall(ms,()=>{S.__krakenEnd===end&&end()})}krakenTentacle(i){const S=this.scene,p=S.player;if(!S.textures.exists("pirate-tentacle"))return;S.anims.exists("pirate-tentacle-slam")||S.anims.create({key:"pirate-tentacle-slam",frames:S.anims.generateFrameNumbers("pirate-tentacle",{start:0,end:5}),frameRate:15,repeat:0});const tg=this.nearestTarget(i.tentacleRange??150),fd=this.facingDir(),dir=tg?Math.sign(tg.x-p.x)||1:fd.x<0?-1:1,x=tg?tg.x-dir*10:p.x+fd.x*46,y=(tg?tg.y:p.y+fd.y*46)+8,sh=S.add.ellipse(x,y,22,7,792617,.6).setDepth(y-1),gl=S.add.image(x,y-2,"light").setBlendMode(j.BlendModes.ADD).setTint(i.color).setScale(.12,.06).setAlpha(.6),t=S.add.sprite(x,y,"pirate-tentacle",0).setOrigin(.35,.97).setDepth(y+1).setAlpha(.9).setFlipX(dir<0);t.play("pirate-tentacle-slam"),S.effects.burstTinted(x,y,i.color,6),S.time.delayedCall(260,()=>{if(!S.scene.isActive())return;const hx=x+dir*14,hy=y-2,{amount:am,crit:cr}=this.rollDamage({damageMult:i.tentacleMult??.9,damageType:"physical"});for(const n of S.combat.getTargets())if(S.damageSystem.circleHit(hx,hy,26,n.x,n.y,(n.body?.width??16)/2)){const d=Math.hypot(n.x-p.x,n.y-p.y)||1;S.damageSystem.apply({target:n,amount:am,critical:cr,type:"physical",dir:{x:(n.x-p.x)/d,y:(n.y-p.y)/d},knockbackMult:.6})}S.effects.burstTinted(hx,hy,9174015,10),S.cameraSys.shake(.003,80)}),t.once("animationcomplete",()=>{S.tweens.add({targets:[t,sh,gl],alpha:0,duration:220,onComplete:()=>{t.destroy(),sh.destroy(),gl.destroy()}})})}'''
rep('execEagle(i){const t=this.scene;', METHODS + 'execEagle(i){const t=this.scene;')

# papagaio reaproveita a águia, com textura, texto e cor próprios
rep('new __Eagle(t,{lifetimeSec:i.duration,radius:i.radius,speed:i.speed})',
    'new __Eagle(t,{lifetimeSec:i.duration,radius:i.radius,speed:i.speed,tex:i.texture,label:i.label,col:i.color})')
rep('this.spr=g.add.sprite(p.x-18,p.y-44,"druid-eagle",0)',
    'this.spr=g.add.sprite(p.x-18,p.y-44,c.tex&&g.textures.exists(c.tex)?c.tex:"druid-eagle",0)')
rep('g.effects.burstTinted(this.spr.x,this.spr.y,11045458,14),g.effects.floatText(p.x,p.y-30,"Águia!","#e8c060",10)',
    'g.effects.burstTinted(this.spr.x,this.spr.y,c.col??11045458,14),g.effects.floatText(p.x,p.y-30,c.label??"Águia!","#e8c060",10)')

# Fúria Pirata é um golpe físico: sem o brilho de "lançar feitiço" nem as faíscas genéricas
rep('["melee-heavy","dash","backstab"].includes(d.type)||', '["melee-heavy","dash","backstab","anchor-slam"].includes(d.type)||')
rep('function __abilityFx(c,i){', 'function __pirateImpact(S,cx,cy,R){const cam=S.cameras.main;S.cameraSys.shake(.022,420),S.effects.hitStop?.(110),S.audioRef?.play("sfx-warrior-heavy-strike"),S.audioRef?.play("sfx-ancient-dragon-meteor");try{const z0=cam.zoom;S.tweens.add({targets:cam,zoom:z0*1.06,duration:70,yoyo:!0,ease:"Quad.easeOut",onComplete:()=>cam.setZoom(z0)})}catch(e){}{const fl=S.add.rectangle(0,0,cam.width*2,cam.height*2,16774630,.22).setOrigin(0).setScrollFactor(0).setDepth(9e4).setBlendMode(j.BlendModes.ADD);S.tweens.add({targets:fl,alpha:0,duration:140,onComplete:()=>fl.destroy()})}if(S.textures.exists("pirate-crater")){const c=S.add.image(cx,cy+2,"pirate-crater").setScale(.62).setDepth(cy-6).setAlpha(0);S.tweens.add({targets:c,alpha:1,scale:.68,duration:90,ease:"Back.easeOut"}),S.tweens.add({targets:c,alpha:0,delay:2200,duration:900,onComplete:()=>c.destroy()})}const mk=(k,a,b,fr)=>{S.anims.exists(k)||S.anims.create({key:k,frames:S.anims.generateFrameNumbers(a,{start:0,end:b}),frameRate:fr,repeat:0})};if(S.textures.exists("pirate-flash")){mk("pirate-flash-pop","pirate-flash",4,26);const f=S.add.sprite(cx,cy-4,"pirate-flash",0).setScale(.9).setDepth(cy+40).setBlendMode(j.BlendModes.ADD);f.play("pirate-flash-pop"),f.once("animationcomplete",()=>f.destroy())}const gl=S.add.image(cx,cy,"light").setBlendMode(j.BlendModes.ADD).setTint(16756810).setScale(.5,.22).setAlpha(.8).setDepth(cy-1);S.tweens.add({targets:gl,alpha:0,scaleX:.9,duration:420,onComplete:()=>gl.destroy()});if(S.textures.exists("pirate-dust")){mk("pirate-dust-roll","pirate-dust",6,13);for(const[dx,sc,dl,dp]of[[0,.7,0,6],[0,.58,60,-3]]){const d=S.add.sprite(cx+dx,cy-8,"pirate-dust",0).setScale(sc).setDepth(cy+dp).setAlpha(.95);S.time.delayedCall(dl,()=>{d.active&&d.play("pirate-dust-roll")}),d.on("animationcomplete",()=>d.destroy())}}if(S.textures.exists("pirate-rocks"))for(let k=0;k<10;k++){const a=-Math.PI*(.08+Math.random()*.84),sp=26+Math.random()*44,vx=Math.cos(a)*sp*(Math.random()<.5?-1:1),hh=14+Math.random()*26,gy=4+Math.random()*10,r=S.add.image(cx,cy-2,"pirate-rocks").setCrop((k%4)*8,0,8,8).setOrigin(((k%4)*8+4)/32,.5).setScale(.9+Math.random()*.6).setDepth(cy+8),o={t:0},spin=(Math.random()-.5)*14;S.tweens.add({targets:o,t:1,duration:520+Math.random()*260,ease:"Linear",onUpdate:()=>{r.setPosition(cx+vx*o.t,cy-2+gy*o.t-hh*4*o.t*(1-o.t)).setRotation(spin*o.t)},onComplete:()=>{S.tweens.add({targets:r,alpha:0,delay:250,duration:300,onComplete:()=>r.destroy()})}})}}' + 'function __abilityFx(c,i){')
rep('function __abilityFx(c,i){__fxTex(c);const p=c.player;if(!p)return;',
    'function __abilityFx(c,i){__fxTex(c);const p=c.player;if(!p||i.type==="anchor-slam")return;')
# ------------------------------------------------------------------ animações configuráveis (layout.fps / map)
# velocidade de cada animação vem do JSON do personagem (padrão do jogo se não houver)
rep('[["idle",e.map.idle,4,-1],["idlevar",e.map.idlevar,3,0],["walk",e.map.walk,11,-1],["run",e.map.run,15,-1]]',
    '[["idle",e.map.idle,e.fps?.idle??4,-1],["idlevar",e.map.idlevar,e.fps?.idlevar??3,0],["walk",e.map.walk,e.fps?.walk??11,-1],["run",e.map.run,e.fps?.run??15,-1]]')
# ataque em várias imagens: cada fase (preparação, golpe, recuperação) percorre a sua lista
# pelo tempo da arma — o dano continua saindo no tempo do jogo, não do quadro
rep('let D;if(this.attackPhase==="windup"){const U=this.weaponDef.anim.windupMs/1e3;',
    'let D;if(M.attackW){const ph=this.attackPhase,L=ph==="windup"?M.attackW:ph==="hit"?M.attackH:M.attackR,an=this.weaponDef.anim,U=(ph==="windup"?an.windupMs:ph==="hit"?an.hitMs:an.recoveryMs)/1e3,pr=U>0?1-this.phaseTimer/U:1;D=L[Math.min(L.length-1,Math.max(0,Math.floor(pr*L.length)))]}else if(this.attackPhase==="windup"){const U=this.weaponDef.anim.windupMs/1e3;')
# morte: toca a sequência inteira uma vez (fps do JSON) e fica no último quadro
rep('this.mk2.anims.stop();const i=this.mk2Layout.map;this.deathFrame=i.deathA,',
    'this.mk2.anims.stop();const i=this.mk2Layout.map;if(i.deathSeq){const fp=this.mk2Layout.fps?.death??9;this.deathFrame=i.deathSeq[0],i.deathSeq.forEach((f,k)=>{k&&this.scene.time.delayedCall(k*1e3/fp,()=>{this.deathFrame=f})});return}this.deathFrame=i.deathA,')
# pose escolhida pela habilidade (Fúria Pirata) tem prioridade sobre andar/parado
rep('this.mk2.setFrame(this.deathFrame??M.deathC??M.deathB);else if(w){',
    'this.mk2.setFrame(this.deathFrame??M.deathC??M.deathB);else if(this.__poseF!=null)this.mk2.anims.stop(),this.mk2.setFrame(this.__poseF);else if(w){')
# salto da Fúria Pirata: o visual sobe sem mexer no corpo físico
rep('t&&(this.container.setPosition(t.x,t.y-2),', 't&&(this.container.setPosition(t.x,t.y-2-(this.__hop||0)),')
# tentáculos a cada ataque básico durante a Ira do Kraken
rep('deliverAttack(i,t,e=null){', 'deliverAttack(i,t,e=null){this.scene.__krakenUntil>this.scene.time.now&&this.scene.__krakenStrike?.();')

# ------------------------------------------------------------------ carregamento de arquivos
rep('["shaman",128,128,"pack"]];', '["shaman",128,128,"pack"],["pirate",128,128,"sep1"]];')
rep('this.load.spritesheet("druid-eagle","assets/pixel-art/characters/druid-eagle.png",{frameWidth:48,frameHeight:48});',
    'this.load.spritesheet("druid-eagle","assets/pixel-art/characters/druid-eagle.png",{frameWidth:48,frameHeight:48});'
    'this.load.spritesheet("pirate-parrot","assets/pixel-art/characters/pirate-parrot.png",{frameWidth:48,frameHeight:48});'
    'this.load.spritesheet("pirate-tentacle","assets/pixel-art/characters/pirate-tentacle.png",{frameWidth:40,frameHeight:64});'
    'this.load.image("pirate-anchor","assets/pixel-art/characters/pirate-anchor2.png");'
    'this.load.image("pirate-crater","assets/pixel-art/characters/pirate-crater.png");'
    'this.load.image("pirate-rocks","assets/pixel-art/characters/pirate-rocks.png");'
    'this.load.spritesheet("pirate-dust","assets/pixel-art/characters/pirate-dust.png",{frameWidth:192,frameHeight:96});'
    'this.load.spritesheet("pirate-flash","assets/pixel-art/characters/pirate-flash.png",{frameWidth:96,frameHeight:96});')
rep('"WOLF_COMPANION"])this.load.image("ix-"+f',
    '"WOLF_COMPANION","FURIA_PIRATA","IRA_KRAKEN","COMPANHEIRO_VOADOR"])this.load.image("ix-"+f')
rep('"necromancer","warlock","shaman","traveler"]){const e=this.cache.json.get(',
    '"necromancer","warlock","shaman","pirate","traveler"]){const e=this.cache.json.get(')
rep('"necromancer","warlock","shaman"],Rl=', '"necromancer","warlock","shaman","pirate"],Rl=')
rep('t("player-shaman",Yi),', 't("player-shaman",Yi),t("player-pirate",Wi),')

# ------------------------------------------------------------------ listas e tabelas por classe
rep('const fe=["WARRIOR","ARCHER","MAGE","ROGUE","NECROMANCER","SHAMAN","BERSERKER","HUNTER","PALADIN"];',
    'const fe=["WARRIOR","ARCHER","MAGE","ROGUE","NECROMANCER","SHAMAN","BERSERKER","PIRATE","HUNTER","PALADIN"];')
rep('const li=["WARRIOR","ARCHER","MAGE","ROGUE","PALADIN","SHAMAN","BERSERKER",',
    'const li=["WARRIOR","ARCHER","MAGE","ROGUE","PALADIN","SHAMAN","BERSERKER","PIRATE",')
rep('PALADIN:"unarmed",SHAMAN:"sword",WARLOCK:"staff"};function Xi', 'PALADIN:"unarmed",SHAMAN:"sword",PIRATE:"great_sword",WARLOCK:"staff"};function Xi')
rep('SHAMAN:{orb:"ui-orb-leather"},BERSERKER:{orb:"ui-orb-leather"},', 'SHAMAN:{orb:"ui-orb-leather"},BERSERKER:{orb:"ui-orb-leather"},PIRATE:{orb:"ui-orb-leather"},')
rep('SHAMAN:{mass:1.05,runLean:3.8,breathHz:1.5,footDust:!0},', 'SHAMAN:{mass:1.05,runLean:3.8,breathHz:1.5,footDust:!0},PIRATE:{mass:1.3,runLean:4.4,breathHz:1.6,footDust:!0},')
rep('SHAMAN:"XAMÃ",WARLOCK:"BRUXO"},lr={', 'SHAMAN:"XAMÃ",PIRATE:"BERSERKER",WARLOCK:"BRUXO"},lr={PIRATE:"BERSERKER",')
rep('vh=new Set(["BERSERKER"])', 'vh=new Set(["BERSERKER","PIRATE"])')
rep('SHAMAN:"shaman_sword",WARLOCK:"bone_staff"};function fi', 'SHAMAN:"shaman_sword",PIRATE:"pirate_cutlass",WARLOCK:"bone_staff"};function fi')
rep('SHAMAN:"#7ee0a0",', 'SHAMAN:"#7ee0a0",PIRATE:"#e86a50",')
rep('const __HN={SHAMAN:"Araí",', 'const __HN={PIRATE:"Capitão Scarpa",SHAMAN:"Araí",')
rep('else if(w==="BERSERKER"){const N=this.scene.resource;', 'else if(w==="BERSERKER"||w==="PIRATE"){const N=this.scene.resource;')

# arma inicial
rep('desc:"Lâmina sagrada consagrada aos espíritos da mata, afiada e leve."},',
    'desc:"Lâmina sagrada consagrada aos espíritos da mata, afiada e leve."},'
    'pirate_cutlass:{name:"Sabre do Capitão",type:"weapon",slot:"weapon",icon:"icon-great-sword",weaponCategory:"BERSERKER",'
    'classRequirement:"PIRATE",weaponClass:"heavy",visualKey:"great_sword",stats:{damage:6},attackSpeed:.75,value:20,'
    'desc:"Sabre curvo de abordagem. Já cortou cordas, velas e muita gente."},')

# textos (pt, en, es)
rep('"class.SHAMAN":"Xamã",', '"class.SHAMAN":"Xamã","class.PIRATE":"Berserker",')
rep('"class.SHAMAN":"Shaman",', '"class.SHAMAN":"Shaman","class.PIRATE":"Berserker",')
rep('"class.SHAMAN":"Chamana",', '"class.SHAMAN":"Chamana","class.PIRATE":"Berserker",')
rep('"tag.BERSERKER":"Disciplina e aço: um corte certo vale mais que dez.",',
    '"tag.BERSERKER":"Disciplina e aço: um corte certo vale mais que dez.",'
    '"tag.PIRATE":"Capitão pirata e berserker: crava a âncora, solta o papagaio e desperta a ira do Kraken.",')
rep('"tag.BERSERKER":"Discipline and steel: one true cut beats ten.",',
    '"tag.BERSERKER":"Discipline and steel: one true cut beats ten.",'
    '"tag.PIRATE":"Pirate captain and berserker: slams the anchor, sends the parrot and wakes the Kraken\'s wrath.",')
rep('"tag.BERSERKER":"Disciplina y acero: un corte certero vale más que diez.",',
    '"tag.BERSERKER":"Disciplina y acero: un corte certero vale más que diez.",'
    '"tag.PIRATE":"Capitán pirata y berserker: clava el ancla, suelta al loro y despierta la ira del Kraken.",')
rep('"desc.BERSERKER":"Katana|Cortes precisos|Espírito",', '"desc.BERSERKER":"Katana|Cortes precisos|Espírito","desc.PIRATE":"Sabre e âncora|Fúria crescente|Papagaio companheiro",')
rep('"desc.BERSERKER":"Katana|Precise cuts|Spirit",', '"desc.BERSERKER":"Katana|Precise cuts|Spirit","desc.PIRATE":"Cutlass and anchor|Rising fury|Parrot companion",')
rep('"desc.BERSERKER":"Katana|Cortes precisos|Espíritu",', '"desc.BERSERKER":"Katana|Cortes precisos|Espíritu","desc.PIRATE":"Sable y ancla|Furia creciente|Loro compañero",')

# ------------------------------------------------------------------ sprites "hiRes"
# O pirata é desenhado em resolução maior (layout.hiRes, escala 0.5). Os pontos abaixo
# usavam tamanho fixo pensado para escala 0.7; com hiRes eles compensam. Sem hiRes
# (todos os outros heróis) o resultado é idêntico ao de antes.
rep('h.setTexture(d,0).setVisible(!0).setOrigin(.5,(J?.footY??119)/128)',
    'h.setTexture(d,0).setVisible(!0).setOrigin(.5,(J?.footY??119)/128).setScale(2*(J?.hiRes?J.scale/.7:1))')
rep('this.por.setTexture(key,0);this.por.setCrop(53,52,22,22).setScale(2).setOrigin(64/128,63/128).setPosition(35,35)',
    'const __J=this.s.cache.json.get(key+"-layout"),__c=__J?.portrait??[53,52,22,22];this.por.setTexture(key,0);'
    'this.por.setCrop(__c[0],__c[1],__c[2],__c[3]).setScale(44/__c[2]).setOrigin((__c[0]+__c[2]/2)/128,(__c[1]+__c[3]/2)/128).setPosition(35,35)')
rep('.setOrigin(.5,(J?.footY??119)/128).setScale(1.1);', '.setOrigin(.5,(J?.footY??119)/128).setScale(1.1*(J?.hiRes?J.scale/.7:1));')
rep('i.hero=i.add.sprite(t/2-30,252,r).setScale(1.3)', 'i.hero=i.add.sprite(t/2-30,252,r).setScale(1.3*(i.heroLayout?.hiRes?i.heroLayout.scale/.7:1))')
rep('this.bodyW=24,this.bodyH=44,', 'this.bodyW=Math.round(24*(this.layout.hiRes?.7/this.layout.scale:1)),this.bodyH=Math.round(44*(this.layout.hiRes?.7/this.layout.scale:1)),')
rep('this.por2.setTexture(p2Key,0);this.por2.setCrop(53,52,22,22).setScale(2).setOrigin(64/128,63/128);',
    'const __J2=this.s.cache.json.get(p2Key+"-layout"),__c2=__J2?.portrait??[53,52,22,22];this.por2.setTexture(p2Key,0);'
    'this.por2.setCrop(__c2[0],__c2[1],__c2[2],__c2[3]).setScale(44/__c2[2]).setOrigin((__c2[0]+__c2[2]/2)/128,(__c2[1]+__c2[3]/2)/128);')

# ------------------------------------------------------------------ painel da seleção de classe
# O commit "revert: remover completamente o modo coop" (8/10) apagou junto o trecho
# que preenche o painel da direita (história, características, atributos e
# habilidades). Restaurado a partir da versão anterior ao coop.
DETAILS = open(os.path.join(ROOT, "scripts", "source", "class-select-details.js"), encoding="utf-8").read()
rep('else h.setVisible(!1)}\nthis.redraw()}__foot(){', 'else h.setVisible(!1)}' + DETAILS + 'this.redraw()}__foot(){')

open(BUNDLE, "w", encoding="utf-8").write(s)
if os.path.isdir(os.path.dirname(MIRROR)):
    shutil.copyfile(BUNDLE, MIRROR)
print("OK — Capitão Scarpa adicionado ao bundle")
