import math

def calculate_bounds(center_lat, center_lon, distance_km):
    """
    Calculate the square bounds of GPS coordinates based on a center point and distance in kilometers.
    
    Args:
    - center_lat: Latitude of the center point in degrees.
    - center_lon: Longitude of the center point in degrees.
    - distance_km: Distance in kilometers for the bounds.
    
    Returns:
    - bounds: Dictionary containing the bounds (north, south, east, west).
    """
    # Approximate value for one degree of latitude in km
    km_per_deg_lat = 111.0
    
    # Calculate change in latitude
    delta_lat = distance_km / km_per_deg_lat
    
    # Convert latitude from degrees to radians
    lat_rad = math.radians(center_lat)
    
    # One degree of longitude in km varies with latitude
    km_per_deg_lon = 111.0 * math.cos(lat_rad)
    delta_lon = distance_km / km_per_deg_lon if km_per_deg_lon != 0 else 0
    
    # Calculate the bounds
    bounds = {
        'north': center_lat + delta_lat,
        'south': center_lat - delta_lat,
        'east': center_lon + delta_lon,
        'west': center_lon - delta_lon
    }

    formatted_bounds = [[bounds['north'],bounds['west']],[bounds['south'],bounds['east']],]
    
    return bounds, formatted_bounds



if __name__ == "__main__":
    # Example usage:
    center_lat = 37.7749  # Center latitude (e.g., San Francisco)
    center_lon = -122.4194  # Center longitude
    distance_km = 22  # Distance in kilometers

    bounds, formatted_bounds = calculate_bounds(center_lat, center_lon, distance_km)

    print(f"North bound: {bounds['north']} degrees")
    print(f"South bound: {bounds['south']} degrees")
    print(f"East bound: {bounds['east']} degrees")
    print(f"West bound: {bounds['west']} degrees")

    print(f"Formatted: {formatted_bounds}")
