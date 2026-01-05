# 17.8 INTERACCION TENSION-CORTANTE

## 17.8.1 Cuando Verificar Interaccion

**No se requiere verificar si:**
- (a) Vua <= 0.2*phi*Vn, o
- (b) Nua <= 0.2*phi*Nn

**Se requiere verificar si:**
- Vua > 0.2*phi*Vn Y Nua > 0.2*phi*Nn

## 17.8.2 Ecuacion de Interaccion Trilineal

```
Nua / (phi*Nn) + Vua / (phi*Vn) <= 1.2     [Ec. 17.8.2]
```

## 17.8.3 Metodo Alternativo - Interaccion Eliptica

Se permite usar:
```
(Nua / (phi*Nn))^(5/3) + (Vua / (phi*Vn))^(5/3) <= 1.0     [Ec. 17.8.3]
```

## Diagrama de Interaccion

```
     Nua/(phi*Nn)
          |
     1.0  +--------+
          |        |\
          |        | \  Lineal (1.2)
          |        |  \
     0.2  +........+...+
          |        |   |
          +--------+---+---- Vua/(phi*Vn)
               0.2   1.0
```

---

*ACI 318-25 Seccion 17.8*
