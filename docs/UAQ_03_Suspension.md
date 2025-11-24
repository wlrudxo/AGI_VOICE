# User Accessible Quantities: Suspension

## 26.8 Bushing

Following quantities describe the quantities which are declared for each bushing component:

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<BushingPre>.t.x/y/z` | - | m | Relative compression along the bushing x,y,z-axis |
| `<BushingPre>.v.x/y/z` | - | m/s | Relative compression velocity along the bushing x,y,z-axis |
| `<BushingPre>.r.x/y/z` | - | rad | Relative rotational compression around the bushing x,y,z-axis |
| `<BushingPre>.Frc.x/y/z` | - | N | Bushing force along the bushing x,y,z-axis |
| `<BushingPre>.Trq.x/y/z` | - | Nm | Bushing torque around the bushing x,y,z-axis |

## 26.8.2 McPherson Suspension

Template variables:
- `<pre> := McPherson.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.DamperL.t` | - | m | Translation of the left damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperL.v` | - | m/s | Translation of the left damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperL.a` | - | m/s² | Translation of the left damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperR.t` | - | m | Translation of the right damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperR.v` | - | m/s | Translation of the right damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.DamperR.a` | - | m/s² | Translation of the right damper relative to the wheel carrier along the thrust damper axis |
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.StbBarL.ra_y` | - | rad/s² | Rotation acceleration of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.rv_y` | - | rad/s | Rotation velocity of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.r_y` | - | rad | Rotation of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.ra_y` | - | rad/s² | Rotation acceleration of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.rv_y` | - | rad/s | Rotation velocity of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.r_y` | - | rad | Rotation of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbLinkL.Bush2WC.*` | - | - | Parameters of the bushing between the left stabilizer link and wheel carrier body |
| `<pre>.StbLinkR.Bush2WC.*` | - | - | Parameters of the bushing between the right stabilizer link and wheel carrier body |
| `<pre>.StbLinkL.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.rv_yx.x/y` | - | rad/s | Rotation velocity of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.r_yx.x/y` | - | rad | Rotation of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.rv_yx.x/y` | - | rad/s | Rotation velocity of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.r_yx.x/y` | - | rad | Rotation of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StrRack.a_y` | - | m/s² | Translation acceleration of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRack.t_y` | - | m | Translation of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRack.v_y` | - | m/s | Translation velocity of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRodL.Bush2StrRack.*` | - | - | Parameters of the bushing between the left steering rod and steering rack body |
| `<pre>.StrRodR.Bush2StrRack.*` | - | - | Parameters of the bushing between the right steering rod and steering rack body |
| `<pre>.StrRodL.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodL.rv_zx.x/z` | - | rad/s | Rotation velocity of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodL.r_zx.x/z` | - | rad | Rotation of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.rv_zx.x/z` | - | rad/s | Rotation velocity of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.r_zx.x/z` | - | rad | Rotation of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.Vhcl.Bush2DampL.*` | - | - | Parameters of the strut bushing between the left damper body and vehicle chassis |
| `<pre>.Vhcl.Bush2DampR.*` | - | - | Parameters of the strut bushing between the right damper body and vehicle chassis |
| `<pre>.WCL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.r_zxy.x/y/z` | - | rad | Rotation of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.t.x/y/z` | - | m | Translation of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.v.x/y/z` | - | m/s | Translation velocity of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.a.x/y/z` | - | m/s² | Translation acceleration of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.r_zxy.x/y/z` | - | rad | Rotation of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.t.x/y/z` | - | m | Translation of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.v.x/y/z` | - | m/s | Translation velocity of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.a.x/y/z` | - | m/s² | Translation acceleration of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WshbL.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the left wishbone body and vehicle chassis |
| `<pre>.WshbL.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the left wishbone body and vehicle chassis |
| `<pre>.WshbL.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the left wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbL.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the left wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbL.r_zyx.x/y/z` | - | rad | Rotation of the left wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbR.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the right wishbone body and vehicle chassis |
| `<pre>.WshbR.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the right wishbone body and vehicle chassis |
| `<pre>.WshbR.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the right wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbR.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the right wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WshbR.r_zyx.x/y/z` | - | rad | Rotation of the right wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |

## 26.8.3 McPherson Suspension with ForceCoupling

At this point only the additional quantities for the stabilizer bar due to the numerical compliance and the resulting forces and torques at the attachment frame are listed. For the description of the other bodies please refer to section 26.8.2.

Template variables:
- `<pre> := McPherson.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.WCL.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.WCR.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.StBarL.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between left stabilizer bar and vehicle chassis |
| `<pre>.StBarR.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between right stabilizer bar and vehicle chassis |
| `<pre>.FrcCpl.Frc_1.x/y/z` | - | N | Resulting forces at attachment frame expressed in Fr1 |
| `<pre>.FrcCpl.Trq_1.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in Fr1 with respect to Fr1 |
| `<pre>.FrcCpl.Frc_Susp.x/y/z` | - | N | Resulting forces at attachment frame expressed in FrSusp |
| `<pre>.FrcCpl.Trq_Susp.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in FrSusp with respect to FrSusp |

## 26.8.4 McPherson Extended Suspension

At this point only the additional quantities for the two bodies subframe and steering box are listed. For the description of the other bodies please refer to section 26.8.2.

Template variables:
- `<pre> := McPherson.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.StrBox.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.rv_zx.x/z` | - | rad/s | Rotation velocity of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.r_zx.x/z` | - | rad | Rotation of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.t.x/y/z` | - | m | Translation of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.StrBox.v.x/y/z` | - | m/s | Translation velocity of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.StrBox.a.x/y/z` | - | m/s² | Translation acceleration of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.Subfrm.BushFL2Vhcl.*` | - | - | Parameters of the front left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushFR2Vhcl.*` | - | - | Parameters of the front right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.BushRL2Vhcl.*` | - | - | Parameters of the rear left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushRR2Vhcl.*` | - | - | Parameters of the rear right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.L2StrBox.*` | - | - | Parameters of the left bushing between the subframe and the steering box body |
| `<pre>.Subfrm.R2StrBox.*` | - | - | Parameters of the right bushing between the subframe and the steering box body |
| `<pre>.Subfrm.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.r_zyx.x/y/z` | - | rad | Rotation of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.t.x/y/z` | - | m | Translation of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.v.x/y/z` | - | m/s | Translation velocity of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.a.x/y/z` | - | m/s² | Translation acceleration of the subframe body relative to the vehicle chassis along the x,y,z-axis |

## 26.8.5 Fourlink Suspension

Template variables:
- `<pre> := FourLink.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.StbBarL.ra_y` | - | rad/s² | Rotation acceleration of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.rv_y` | - | rad/s | Rotation velocity of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.r_y` | - | rad | Rotation of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.ra_y` | - | rad/s² | Rotation acceleration of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.rv_y` | - | rad/s | Rotation velocity of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.r_y` | - | rad | Rotation of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbLinkL.Bush.*` | - | - | Parameters of the bushing between the left stabilizer link and wheel carrier (or lower wishbone) body |
| `<pre>.StbLinkL.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.rv_yx.x/y` | - | rad/s | Rotation velocity of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.r_yx.x/y` | - | rad | Rotation of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.Bush.*` | - | - | Parameters of the bushing between the right stabilizer link and wheel carrier (or lower wishbone) body |
| `<pre>.StbLinkR.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.rv_yx.x/y` | - | rad/s | Rotation velocity of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.r_yx.x/y` | - | rad | Rotation of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StrRodL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left steering rod body and vehicle chassis |
| `<pre>.StrRodL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.r_zxy.x/y/z` | - | rad | Rotation of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right steering rod body and vehicle chassis |
| `<pre>.StrRodR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.r_zxy.x/y/z` | - | rad | Rotation of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left trailing arm body and vehicle chassis |
| `<pre>.TrailArmL.ra_z` | - | rad/s² | Rotation acceleration of the left trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmL.rv_z` | - | rad/s | Rotation velocity of the left trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmL.r_z` | - | rad | Rotation of the left trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmL.Trq2WC_z` | - | Nm | Spring-damper torque of the left trailing arm body |
| `<pre>.TrailArmR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right trailing arm body and vehicle chassis |
| `<pre>.TrailArmR.ra_z` | - | rad/s² | Rotation acceleration of the right trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmR.rv_z` | - | rad/s | Rotation velocity of the right trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmR.r_z` | - | rad | Rotation of the right trailing arm relative to wheel carrier body around the z-axis |
| `<pre>.TrailArmR.Trq2WC_z` | - | Nm | Spring-damper torque of the right trailing arm body |
| `<pre>.WCL.a.x/y/z` | - | m/s² | Translation acceleration of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.r_zxy.x/y/z` | - | rad | Rotation of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.t.x/y/z` | - | m | Translation of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.v.x/y/z` | - | m/s | Translation velocity of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.a.x/y/z` | - | m/s² | Translation acceleration of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.r_zxy.x/y/z` | - | rad | Rotation of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.t.x/y/z` | - | m | Translation of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.v.x/y/z` | - | m/s | Translation velocity of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WishLowL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left lower wishbone body and vehicle chassis |
| `<pre>.WishLowL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.r_zxy.x/y/z` | - | rad | Rotation of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right lower wishbone body and vehicle chassis |
| `<pre>.WishLowR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.r_zxy.x/y/z` | - | rad | Rotation of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left upper wishbone body and vehicle chassis |
| `<pre>.WishUppL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.r_zxy.x/y/z` | - | rad | Rotation of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right upper wishbone body and vehicle chassis |
| `<pre>.WishUppR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.r_zxy.x/y/z` | - | rad | Rotation of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |

## 26.8.6 Fourlink Suspension with ForceCoupling

At this point only the additional quantities for the stabilizer bar due to the numerical compliance and the resulting forces and torques at the attachment frame are listed. For the description of the other bodies please refer to section 26.8.5.

Template variables:
- `<pre> := FourLink.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.WCL.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.WCR.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.StBarL.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between left stabilizer bar and vehicle chassis |
| `<pre>.StBarR.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between right stabilizer bar and vehicle chassis |
| `<pre>.FrcCpl.Frc_1.x/y/z` | - | N | Resulting forces at attachment frame expressed in Fr1 |
| `<pre>.FrcCpl.Trq_1.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in Fr1 with respect to Fr1 |
| `<pre>.FrcCpl.Frc_Susp.x/y/z` | - | N | Resulting forces at attachment frame expressed in FrSusp |
| `<pre>.FrcCpl.Trq_Susp.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in FrSusp with respect to FrSusp |

## 26.8.7 Fourlink Extended Suspension

At this point only the additional quantities for the body subframe are listed. For the description of the other bodies please refer to section 26.8.5.

Template variables:
- `<pre> := FourLink.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.Subfrm.BushFL2Vhcl.*` | - | - | Parameters of the front left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushFR2Vhcl.*` | - | - | Parameters of the front right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.BushRL2Vhcl.*` | - | - | Parameters of the rear left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushRR2Vhcl.*` | - | - | Parameters of the rear right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.r_zyx.x/y/z` | - | rad | Rotation of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.t.x/y/z` | - | m | Translation of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.v.x/y/z` | - | m/s | Translation velocity of the subframe body relative to the vehicle chassis along the x,y,z-axis |

## 26.8.8 Fourlink Modified Extended Suspension

Template variables:
- `<pre> := FourLink.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.StbBarL.ra_y` | - | rad/s² | Rotation acceleration of the left stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarL.rv_y` | - | rad/s | Rotation velocity of the left stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarL.r_y` | - | rad | Rotation of the left stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarR.ra_y` | - | rad/s² | Rotation acceleration of the right stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarR.rv_y` | - | rad/s | Rotation velocity of the right stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbBarR.r_y` | - | rad | Rotation of the right stabilizer bar body relative to subframe body around the y-axis |
| `<pre>.StbLinkL.Bush.*` | - | - | Parameters of the bushing between the left stabilizer link and wheel carrier (or lower/upper wishbone) body |
| `<pre>.StbLinkL.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.rv_yx.x/y` | - | rad/s | Rotation velocity of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.r_yx.x/y` | - | rad | Rotation of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.Bush.*` | - | - | Parameters of the bushing between the right stabilizer link and wheel carrier (or lower/upper wishbone) body |
| `<pre>.StbLinkR.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.rv_yx.x/y` | - | rad/s | Rotation velocity of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.r_yx.x/y` | - | rad | Rotation of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StrRodL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left steering rod body and subframe body |
| `<pre>.StrRodL.a.x/y/z` | - | m/s² | Translation acceleration of the left steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.r_zxy.x/y/z` | - | rad | Rotation of the left steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodL.t.x/y/z` | - | m | Translation of the left steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodL.v.x/y/z` | - | m/s | Translation velocity of the left steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right steering rod body and subframe body |
| `<pre>.StrRodR.a.x/y/z` | - | m/s² | Translation acceleration of the right steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.r_zxy.x/y/z` | - | rad | Rotation of the right steering rod relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.StrRodR.t.x/y/z` | - | m | Translation of the right steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.StrRodR.v.x/y/z` | - | m/s | Translation velocity of the right steering rod body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.Subfrm.BushFL2Vhcl.*` | - | - | Parameters of the front left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushFR2Vhcl.*` | - | - | Parameters of the front right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.BushRL2Vhcl.*` | - | - | Parameters of the rear left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushRR2Vhcl.*` | - | - | Parameters of the rear right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.r_zyx.x/y/z` | - | rad | Rotation of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.t.x/y/z` | - | m | Translation of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.v.x/y/z` | - | m/s | Translation velocity of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.a.x/y/z` | - | m/s² | Translation acceleration of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.TrailArmL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left trailing arm body and the subframe body |
| `<pre>.TrailArmL.a.x/y/z` | - | m/s² | Translation acceleration of the left trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmL.r_zxy.x/y/z` | - | rad | Rotation of the left trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmL.t.x/y/z` | - | m | Translation of the left trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmL.v.x/y/z` | - | m/s | Translation velocity of the left trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right trailing arm body and the subframe body |
| `<pre>.TrailArmR.a.x/y/z` | - | m/s² | Translation acceleration of the right trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmR.r_zxy.x/y/z` | - | rad | Rotation of the right trailing arm relative to the wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.TrailArmR.t.x/y/z` | - | m | Translation of the right trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.TrailArmR.v.x/y/z` | - | m/s | Translation velocity of the right trailing arm body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WCL.Bush2WishLow.*` | - | - | Parameters of the bushing between the left lower wishbone body and the wheel carrier body |
| `<pre>.WCL.Bush2TrailArm.*` | - | - | Parameters of the bushing between the left trailing arm body and the wheel carrier body |
| `<pre>.WCL.Bush2SteerRod.*` | - | - | Parameters of the bushing between the left steering rod body and the wheel carrier body |
| `<pre>.WCL.a.x/y/z` | - | m/s² | Translation acceleration of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.r_zxy.x/y/z` | - | rad | Rotation of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.t.x/y/z` | - | m | Translation of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.v.x/y/z` | - | m/s | Translation velocity of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.Bush2WishLow.*` | - | - | Parameters of the bushing between the right lower wishbone body and the wheel carrier body |
| `<pre>.WCR.Bush2TrailArm.*` | - | - | Parameters of the bushing between the right trailing arm body and the wheel carrier body |
| `<pre>.WCR.Bush2SteerRod.*` | - | - | Parameters of the bushing between the right steering rod body and the wheel carrier body |
| `<pre>.WCR.a.x/y/z` | - | m/s² | Translation acceleration of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.r_zxy.x/y/z` | - | rad | Rotation of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.t.x/y/z` | - | m | Translation of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.v.x/y/z` | - | m/s | Translation velocity of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WishLowL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left lower wishbone body and the subframe body |
| `<pre>.WishLowL.a.x/y/z` | - | m/s² | Translation acceleration of the left lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.r_zxy.x/y/z` | - | rad | Rotation of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowL.t.x/y/z` | - | m | Translation of the left lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowL.v.x/y/z` | - | m/s | Translation velocity of the left lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right lower wishbone body and the subframe body |
| `<pre>.WishLowR.a.x/y/z` | - | m/s² | Translation acceleration of the right lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.r_zxy.x/y/z` | - | rad | Rotation of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishLowR.t.x/y/z` | - | m | Translation of the right lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishLowR.v.x/y/z` | - | m/s | Translation velocity of the right lower wishbone body relative to left wheel carrier body along the x,y,z-axis |
| `<pre>.WishUppL.BushF2Vhcl.*` | - | - | Parameters of the bushing between the left front upper wishbone body and the subframe body |
| `<pre>.WishUppL.BushR2Vhcl.*` | - | - | Parameters of the bushing between the left rear upper wishbone body and the subframe body |
| `<pre>.WishUppL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppL.r_zxy.x/y/z` | - | rad | Rotation of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.BushF2Vhcl.*` | - | - | Parameters of the bushing between the right front upper wishbone body and the subframe body |
| `<pre>.WishUppR.BushR2Vhcl.*` | - | - | Parameters of the bushing between the right rear upper wishbone body and the subframe body |
| `<pre>.WishUppR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WishUppR.r_zxy.x/y/z` | - | rad | Rotation of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZXY |

## 26.8.9 Twistrbeam Suspension

Template variables:
- `<pre> := TwistBeam.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.TorsBeam.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the torsion beam body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TorsBeam.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the torsion beam body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TorsBeam.r_zyx.x/y/z` | - | rad | Rotation of the torsion beam body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TorsBeam.t.x/y/z` | - | m | Translation of the torsion beam body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.TorsBeam.v.x/y/z` | - | m/s | Translation velocity of the torsion beam body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.TorsBeam.a.x/y/z` | - | m/s² | Translation acceleration of the torsion beam body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.TrlArmL.Bush2Vhcl.*` | - | - | Parameters of the bushing between the left trailing arm body and vehicle chassis |
| `<pre>.TrlArmL.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the left trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmL.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the left trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmL.r_zyx.x/y/z` | - | rad | Rotation of the left trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmL.Trq2TorsBeam.x/y/z` | - | Nm | Spring-damper torque of the left trailing arm body to the torsion beam around the x,y,z-axis |
| `<pre>.TrlArmR.Bush2Vhcl.*` | - | - | Parameters of the bushing between the right trailing arm body and vehicle chassis |
| `<pre>.TrlArmR.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the right trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmR.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the right trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmR.r_zyx.x/y/z` | - | rad | Rotation of the right trailing arm body relative to torsion beam around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.TrlArmR.Trq2TorsBeam.x/y/z` | - | Nm | Spring-damper torque of the right trailing arm body to the torsion beam around the x,y,z-axis |
| `<pre>.WCL.ra_z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCL.rv_z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCL.r_z` | - | rad | Rotation of the left wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCL.Trq2TrailArm_z` | - | Nm | Spring-damper torque of the left wheel carrier body to trailing arm body |
| `<pre>.WCR.ra_z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCR.rv_z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCR.r_z` | - | rad | Rotation of the right wheel carrier body relative to trailing arm body around the z-axis |
| `<pre>.WCR.Trq2TrailArm_z` | - | Nm | Spring-damper torque of the right wheel carrier body to trailing arm body |

## 26.8.10 Twistrbeam Extended Suspension

At this point only the quantities for the additional model elements are listed. For the description of the other bodies please refer to section 26.8.9.

Template variables:
- `<pre> := TwistBeam.<pos>`
- `<pos> := SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.TrlArmL.Bush2TorsBeam.*` | - | - | Parameters of the bushing between the left trailing arm body and the torsion beam body |
| `<pre>.TrlArmL.t.x/y/z` | - | m | Translation of the left trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmL.v.x/y/z` | - | m/s | Translation velocity of the left trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmL.a.x/y/z` | - | m/s² | Translation acceleration of the left trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmR.Bush2TorsBeam.*` | - | - | Parameters of the bushing between the right trailing arm body and the torsion beam body |
| `<pre>.TrlArmR.t.x/y/z` | - | m | Translation of the right trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmR.v.x/y/z` | - | m/s | Translation velocity of the right trailing arm body relative to the torsion beam along the x,y,z-axis |
| `<pre>.TrlArmR.a.x/y/z` | - | m/s² | Translation acceleration of the right trailing arm body relative to the torsion beam along the x,y,z-axis |

## 26.8.11 Double Wishbone Suspension

Template variables:
- `<pre> := DoubleWishbone.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.OSRate` | - | - | Model oversampling rate (integer) |
| `<pre>.PlungL.Frc2Wheel` | - | N | Normal force at the left tire contact point |
| `<pre>.PlungR.Frc2Wheel` | - | N | Normal force at the right tire contact point |
| `<pre>.StbBarL.ra_y` | - | rad/s² | Rotation acceleration of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.rv_y` | - | rad/s | Rotation velocity of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarL.r_y` | - | rad | Rotation of the left stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.ra_y` | - | rad/s² | Rotation acceleration of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.rv_y` | - | rad/s | Rotation velocity of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbBarR.r_y` | - | rad | Rotation of the right stabilizer bar body relative to vehicle chassis around the y-axis |
| `<pre>.StbLinkL.Bush2WC.*` | - | - | Parameters of the bushing between the left stabilizer link and wheel carrier body |
| `<pre>.StbLinkR.Bush2WC.*` | - | - | Parameters of the bushing between the right stabilizer link and wheel carrier body |
| `<pre>.StbLinkL.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.rv_yx.x/y` | - | rad/s | Rotation velocity of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkL.r_yx.x/y` | - | rad | Rotation of the left stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.ra_yx.x/y` | - | rad/s² | Rotation acceleration of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.rv_yx.x/y` | - | rad/s | Rotation velocity of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StbLinkR.r_yx.x/y` | - | rad | Rotation of the right stabilizer link body relative to stabilizer bar around the x,y-axis with rotation sequence YX |
| `<pre>.StrRack.a_y` | - | m/s² | Translation acceleration of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRack.t_y` | - | m | Translation of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRack.v_y` | - | m/s | Translation velocity of the steering rack body relative to the vehicle chassis along the y-axis (information imposed by steering model) |
| `<pre>.StrRodL.Bush2StrRack.*` | - | - | Parameters of the bushing between the left steering rod and steering rack body |
| `<pre>.StrRodR.Bush2StrRack.*` | - | - | Parameters of the bushing between the right steering rod and steering rack body |
| `<pre>.StrRodL.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodL.rv_zx.x/z` | - | rad/s | Rotation velocity of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodL.r_zx.x/z` | - | rad | Rotation of the left steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.rv_zx.x/z` | - | rad/s | Rotation velocity of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrRodR.r_zx.x/z` | - | rad | Rotation of the right steering rod relative to the wheel carrier body around the x,z-axis with rotation sequence ZX |
| `<pre>.Vhcl.Bush2DampL.*` | - | - | Parameters of the strut bushing between the left damper body and vehicle chassis |
| `<pre>.Vhcl.Bush2DampR.*` | - | - | Parameters of the strut bushing between the right damper body and vehicle chassis |
| `<pre>.WCL.a.x/y/z` | - | m/s² | Translation acceleration of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.r_zxy.x/y/z` | - | rad | Rotation of the left wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCL.t.x/y/z` | - | m | Translation of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCL.v.x/y/z` | - | m/s | Translation velocity of the left wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.a.x/y/z` | - | m/s² | Translation acceleration of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.ra_zxy.x/y/z` | - | rad/s² | Rotation acceleration of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.rv_zxy.x/y/z` | - | rad/s | Rotation velocity of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.r_zxy.x/y/z` | - | rad | Rotation of the right wheel carrier body relative to vehicle chassis around the x,y,z-axis with rotation sequence ZXY |
| `<pre>.WCR.t.x/y/z` | - | m | Translation of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WCR.v.x/y/z` | - | m/s | Translation velocity of the right wheel carrier body relative to vehicle chassis along the x,y,z-axis |
| `<pre>.WishLowL.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the left lower wishbone body and vehicle chassis |
| `<pre>.WishLowL.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the left lower wishbone body and vehicle chassis |
| `<pre>.WishLowL.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowL.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowL.r_zyx.x/y/z` | - | rad | Rotation of the left lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowR.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the right lower wishbone body and vehicle chassis |
| `<pre>.WishLowR.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the right lower wishbone body and vehicle chassis |
| `<pre>.WishLowR.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowR.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishLowR.r_zyx.x/y/z` | - | rad | Rotation of the right lower wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppL.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the left upper wishbone body and vehicle chassis |
| `<pre>.WishUppL.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the left upper wishbone body and vehicle chassis |
| `<pre>.WishUppL.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppL.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppL.r_zyx.x/y/z` | - | rad | Rotation of the left upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppR.BushF2Vhcl.*` | - | - | Parameters of the front bushing between the right upper wishbone body and vehicle chassis |
| `<pre>.WishUppR.BushR2Vhcl.*` | - | - | Parameters of the rear bushing between the right upper wishbone body and vehicle chassis |
| `<pre>.WishUppR.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppR.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.WishUppR.r_zyx.x/y/z` | - | rad | Rotation of the right upper wishbone relative to wheel carrier body around the x,y,z-axis with rotation sequence ZYX |

## 26.8.12 Double Wishbone Suspension with ForceCoupling

At this point only the additional quantities for the stabilizer bar due to the numerical compliance and the resulting forces and torques at the attachment frame are listed. For the description of the other bodies please refer to section 26.8.11.

Template variables:
- `<pre> := DoubleWishbone.<pos>`
- `<pos> := SuspF, SuspR`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.WCL.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.WCR.*` | - | - | All quantities describing the motion of the wheel carrier bodies are expressed in Fr0 with respect to Fr0 |
| `<pre>.StBarL.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between left stabilizer bar and vehicle chassis |
| `<pre>.StBarR.Bush2Vhcl.*` | - | - | Parameters of numerical bushing between right stabilizer bar and vehicle chassis |
| `<pre>.FrcCpl.Frc_1.x/y/z` | - | N | Resulting forces at attachment frame expressed in Fr1 |
| `<pre>.FrcCpl.Trq_1.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in Fr1 with respect to Fr1 |
| `<pre>.FrcCpl.Frc_Susp.x/y/z` | - | N | Resulting forces at attachment frame expressed in FrSusp |
| `<pre>.FrcCpl.Trq_Susp.x/y/z` | - | Nm | Resulting torques at attachment frame expressed in FrSusp with respect to FrSusp |

## 26.8.13 Double Wishbone Extended Suspension

At this point only the additional quantities for the two bodies subframe and steering box are listed. For the description of the other bodies please refer to section 26.8.11.

Template variables:
- `<pre> := DoubleWishbone.<pos>`
- `<pos> := SuspF`

| UAQ Name | C-Code | Unit | Info |
|---|---|---|---|
| `<pre>.StrBox.ra_zx.x/z` | - | rad/s² | Rotation acceleration of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.rv_zx.x/z` | - | rad/s | Rotation velocity of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.r_zx.x/z` | - | rad | Rotation of the steering box relative to the subframe body around the x,z-axis with rotation sequence ZX |
| `<pre>.StrBox.t.x/y/z` | - | m | Translation of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.StrBox.v.x/y/z` | - | m/s | Translation velocity of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.StrBox.a.x/y/z` | - | m/s² | Translation acceleration of the steering box relative to the subframe body along the x,y,z-axis |
| `<pre>.Subfrm.BushFL2Vhcl.*` | - | - | Parameters of the front left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushFR2Vhcl.*` | - | - | Parameters of the front right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.BushRL2Vhcl.*` | - | - | Parameters of the rear left bushing between the subframe body and vehicle chassis |
| `<pre>.Subfrm.BushRR2Vhcl.*` | - | - | Parameters of the rear right bushing between the subframe and vehicle chassis |
| `<pre>.Subfrm.L2StrBox.*` | - | - | Parameters of the left bushing between the subframe and the steering box body |
| `<pre>.Subfrm.R2StrBox.*` | - | - | Parameters of the right bushing between the subframe and the steering box body |
| `<pre>.Subfrm.ra_zyx.x/y/z` | - | rad/s² | Rotation acceleration of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.rv_zyx.x/y/z` | - | rad/s | Rotation velocity of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.r_zyx.x/y/z` | - | rad | Rotation of the subframe body relative to the vehicle chassis around the x,y,z-axis with rotation sequence ZYX |
| `<pre>.Subfrm.t.x/y/z` | - | m | Translation of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.v.x/y/z` | - | m/s | Translation velocity of the subframe body relative to the vehicle chassis along the x,y,z-axis |
| `<pre>.Subfrm.a.x/y/z` | - | m/s² | Translation acceleration of the subframe body relative to the vehicle chassis along the x,y,z-axis |

---

**Document Information:**
- Source: CarMaker Reference Manual Version 14.0
- Category: MBS Suspension
- Section: User Accessible Quantities
- Generated from: UAQ_03_Suspension.txt
- Conversion completed with ligature fixes (fl, fi) and vector component normalization (x/y/z notation)
