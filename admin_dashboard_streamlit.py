import streamlit as st 
import folium 
from streamlit_folium import st_folium
import requests
import pandas as pd




def get_color_and_pci(pci_type, pci_score, velocity):
    color_dict={
        1.0: 'green',
        2.0: 'blue',
        3.0: 'yellow',
        4.0: 'orange',
        5.0: 'red'
    }
    if pci_type == "Prediction based":
        return color_dict[pci_score], pci_score
    elif pci_type == "Velocity Based":
        if 0<=velocity<2.78:
            return color_dict[5.0], 5.0
        elif 2.78<=velocity<5.56:
            return color_dict[4.0], 4.0
        elif 5.56<=velocity<8.34:
            return color_dict[3.0], 3.0
        elif 8.34<=velocity<10:
            return color_dict[2.0], 2.0
        elif velocity>=10:
            return color_dict[1.0], 1.0 
        



@st.cache_data
def get_data():
    map_data = requests.get('http://13.201.2.105/get_data_dump')
    # map_data = requests.get('http://127.0.0.1:5000/get_data_dump')
    return map_data.json()

@st.cache_data
def get_user_names():
    data = get_data()
    users = set(entry[0] for entry in data)
    return users


st.title('ROAD QUALITY DASHBOARD')

def get_avg_vel(old_data, v_new, s_new):
    v_old = old_data['avg_velocity']
    s_old = old_data['distance_travelled']
    # print(type(v_old), type(v_new), type(s_old), type(s_new))
    if v_old != 0:
        avg_vel = (s_old+s_new)/((s_old/v_old)+(s_new/v_new))
        return avg_vel * 18/5
    else:
        return v_new * 18/5
    
@st.cache_data
def get_stats(user_data):
    stat_dict = {
        1: {
            'number_of_segments': 0,
            'distance_travelled': 0,
            'avg_velocity': 0
        },
        2: {
            'number_of_segments': 0,
            'distance_travelled': 0,
            'avg_velocity': 0
        },
        3: {
            'number_of_segments': 0,
            'distance_travelled': 0,
            'avg_velocity': 0
        },
        4: {
            'number_of_segments': 0,
            'distance_travelled': 0,
            'avg_velocity': 0
        },
        5: {
            'number_of_segments': 0,
            'distance_travelled': 0,
            'avg_velocity': 0
        },
    }
    for entry in user_data:
        stat_dict[entry[1]]['number_of_segments']+=1
        stat_dict[entry[1]]['distance_travelled']+=entry[4]/1000
        stat_dict[entry[1]]['avg_velocity'] = get_avg_vel(stat_dict[entry[1]], entry[2], entry[4])
    
    return stat_dict

@st.cache_data
def user_details(user_name):
    data = get_data()
    user_data = [item for item in data if item[0]==user_name]
    stats = get_stats(user_data)
    return stats

checkbox_states = {}
with st.sidebar:
    st.write("Select Users: ")
    items = get_user_names()
    for item in items:
        checkbox_states[item] = st.checkbox(item, True)

pci_type = st.radio(
    "***Select PCI type:***", 
    ["Prediction based", "Velocity Based"]
)

# st.divider()
# st.markdown('#### Legend')

# user_names = get_user_names()
# st.multiselect(
#     "***Select Users:***",
#     get_user_names(),
#     get_user_names()
# )

st.divider()
st.header('Map with labeled roads')


m = folium.Map(location=[16.8557,73.5453], zoom_start=14)
data = get_data()

for entry in data:
    if checkbox_states[entry[0]]:
        col, pci = get_color_and_pci(pci_type, entry[1], entry[2])
        folium.PolyLine(
            locations=entry[3], 
            color = col, #color_dict[entry[0]]
            # tooltip=f"avg_velocity: {entry[2]}, PCI score: {pci}", 
            tooltip=folium.Tooltip(f"avg_velocity: {entry[2]}, PCI score: {pci}, length: {entry[4]}", sticky=True),
            thickness = 20, 
        ).add_to(m)
    
st_folium(m, width=725, returned_objects=[])

st.divider()

# def write_user_wise_stat(user_name):
#     st.markdown(f"##### {user_name}")
#     stats = user_details(user_name)
#     for key, value in stats.items():
#         st.markdown(f"###### PCI: {key}")
#         st.markdown(f"number of segments: {value['number_of_segments']}")
#         st.markdown(f"distance travelled: {value['distance_travelled']}")
#         st.markdown(f"avg speed: {value['avg_velocity']}")

def write_user_wise_stat(user_name):
    st.markdown(f"##### {user_name}")
    stats = user_details(user_name)
    
    # Prepare data for the table
    table_data = []
    for key, value in stats.items():
        table_data.append({
            'PCI': key,
            'Number of Segments': value['number_of_segments'],
            'Distance Travelled(Km)': value['distance_travelled'],
            'Avg Speed(Km/hr)': value['avg_velocity']
        })
    
    # Convert to DataFrame
    df = pd.DataFrame(table_data)
    
    # Display the table
    st.table(df)

for key, value in checkbox_states.items():
    if value:
        write_user_wise_stat(key)
        st.divider()



    

        

# st.write(get_data())
# print(get_data)
    # print(map_data)
# center on Liberty Bell, add marker
# m = folium.Map(location=[19.1352249, 72.9096006], zoom_start=16)
# folium.Marker(
#     [39.949610, -75.150282]
# ).add_to(m)



# call to render Folium map in Streamlit, but don't get any data back
# from the map (so that it won't rerun the app when the user interacts)
# st_folium(m, width=725, returned_objects=[])
