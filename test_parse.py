from fetch_ihmcl import parse, month_of
L = ["Gegal Ajmer Jaipur 5,08,445 1,75,53,055 24,890 26,01,420 81,096 1,74,28,800 23,069 82,78,445 2,12,004 7,72,51,730 244 88,390 8,49,748 12,32,01,840",
"Gardiya Toll Plaza Jaisalmer Jaipur 34 2,120 - - 1 270 - - 3 1,275 - - 38 3,665",
"PLAZA_NAME PIU RO CAR_JEEP_CNT CAR_JEEP_AMT",
"VC Wise Monthly ETC FASTag Data for the Month of Sept 2026"]
r = parse("\n".join(L), "2026-09"); assert len(r) == 2, r
g = r[0]; assert g["l"] == "Gegal Ajmer Jaipur" and g["lcv"] == 24890 and g["bt"] == 81096 and g["a3"] == 23069 and g["a4"] == 212004 and g["t"] == 849748 and g["c"] == 508445
assert r[1]["lcv"] == 0 and r[1]["bt"] == 1 and r[1]["t"] == 38
U = {"https://ihmcl.co.in/wp-content/uploads/2026/10/VC-wise-ETC-Data-Sept-2026.pdf": "2026-09",
"https://ihmcl.co.in/wp-content/uploads/2026/08/Jul-2026-1.pdf": "2026-07",
"https://ihmcl.co.in/wp-content/uploads/2025/09/Aug-2025-ETC-Data.pdf": "2025-08",
"https://ihmcl.co.in/wp-content/uploads/2026/10/Set-2026-Annual-Pass-Data.pdf": None,
"https://ihmcl.co.in/wp-content/uploads/2026/09/VC_Wise_Monthly_Data_Aug_2026.pdf": None,
"https://ihmcl.co.in/wp-content/uploads/2026/10/ANNUAL-REPORT-2025-26.pdf": None,
"https://ihmcl.co.in/wp-content/uploads/2026/10/Fastag-Booklet-.pdf": None,
"https://ihmcl.co.in/wp-content/uploads/2026/06/MLFF-Plaza-Data-May-26_v1.pdf": None}
for u, e in U.items(): assert month_of(u) == e, (u, month_of(u))
print("python tests ok")
