from graph_builder import build_graph

app = build_graph()

state = {
    "image_url": "https://analysisstorage.blob.core.windows.net/images/sample5.jpeg?sp=r&st=2026-03-01T07:09:25Z&se=2026-03-01T15:24:25Z&sv=2024-11-04&sr=b&sig=L1CAN%2BnvawhebZriqd%2FQTOIrpXyY1KUuVgcBaZNBNuY%3D"
}

print("\n===== STREAMING EXECUTION =====\n")

for event in app.stream(state):
    print(event)
    print("--------------------------------------------------")
