import os
import pandas as pd

def decode_hex(hex_string):
    if pd.isna(hex_string) or hex_string is None:
        return ""
    
    val_str = str(hex_string).strip()
    if val_str == "" or val_str.upper() == "NULL":
        return ""
        
    try:
        # Try standard hex decoding
        decoded = bytes.fromhex(val_str).decode('utf-8').strip()
        
        if decoded.lower() in ["inf", "-inf", "infinity", "-infinity"]:
            return ""
            
        try:
            num = float(decoded)
            if num.is_integer():
                return str(int(num))
            return str(num)
        except ValueError:
            return decoded
            
    except ValueError:
        # CRITICAL PROTECTION: If it's not valid hex (like '96168204949'), 
        # keep it exactly as it is so no raw data disappears!
        if val_str.lower() in ["inf", "-inf", "infinity", "-infinity"]:
            return ""
        return val_str

def convert_csv_to_csv(csv_file_path, output_csv_path):
    print(f"\n[1/3] Checking file structure for {csv_file_path}...")
    
    # AUTO-DETECT DELIMITER: Inspect the first line to see if it uses commas, semicolons, or tabs
    chosen_sep = ','
    try:
        with open(csv_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()
            if ';' in first_line and first_line.count(';') > first_line.count(','):
                chosen_sep = ';'
            elif '\t' in first_line:
                chosen_sep = '\t'
        print(f" -> Automatically detected separator: {repr(chosen_sep)}")
    except Exception:
        print(" -> Defaulting to standard comma separator.")

    # Read strictly as raw string text
    df = pd.read_csv(csv_file_path, sep=chosen_sep, dtype=str, keep_default_na=False, na_filter=False)
    
    # Process column renames smoothly regardless of Excel header truncation
    csv_columns = df.columns.tolist()
    clean_columns = {}
    for col in csv_columns:
        c_low = col.lower()
        if c_low.endswith('_hex'):
            clean_columns[col] = col[:-4]
        elif c_low.endswith('_h') and ('lat' in c_low or 'thre' in c_low or 'warn' in c_low):
            clean_columns[col] = col[:-2]
        elif c_low == 'longitude_':
            clean_columns[col] = 'longitude'
        else:
            clean_columns[col] = col
            
    print(f"[2/3] Decoding data matrix safely...")
    for col in csv_columns:
        df[col] = df[col].apply(decode_hex)
        
    df = df.rename(columns=clean_columns)
    
    print(f"[3/3] Writing standardized output back to disk...")
    df.to_csv(output_csv_path, index=False, sep=',')
    print(f"\n✨ Success! All data recovered and saved to: {output_csv_path}")

# ==========================================
# CHOICE 2: CSV ➡️ SQL FILE
# ==========================================
def convert_csv_to_sql(csv_file_path, output_sql_path):
    print(f"\n[1/3] Reading source CSV file dynamically...")
    chosen_sep = ','
    try:
        with open(csv_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_line = f.readline()
            if ';' in first_line and first_line.count(';') > first_line.count(','):
                chosen_sep = ';'
            elif '\t' in first_line:
                chosen_sep = '\t'
    except Exception:
        pass

    df = pd.read_csv(csv_file_path, sep=chosen_sep, dtype=str, keep_default_na=False, na_filter=False)
    csv_columns = df.columns.tolist()
    
    sql_columns = []
    cleaned_col_names = []
    for col in csv_columns:
        c_low = col.lower()
        if c_low.endswith('_hex'): clean_name = col[:-4]
        elif c_low.endswith('_h') and ('lat' in c_low or 'thre' in c_low or 'warn' in c_low): clean_name = col[:-2]
        elif c_low == 'longitude_': clean_name = 'longitude'
        else: clean_name = col
        
        cleaned_col_names.append(f"`{clean_name}`")
        
        if 'lat' in clean_name.lower() or 'long' in clean_name.lower():
            sql_columns.append(f"    `{clean_name}` DECIMAL(10, 6) DEFAULT NULL")
        elif 'thre' in clean_name.lower() or 'normal' in clean_name.lower(): 
            sql_columns.append(f"    `{clean_name}` VARCHAR(50) DEFAULT NULL")
        else:
            sql_columns.append(f"    `{clean_name}` TEXT")

    sql_statements = [
        "DROP TABLE IF EXISTS `telemetry_readings`;",
        "CREATE TABLE `telemetry_readings` (",
        "    `id` INT AUTO_INCREMENT PRIMARY KEY,",
        ",\n".join(sql_columns),
        ");\n",
        f"INSERT INTO `telemetry_readings` ({', '.join(cleaned_col_names)}) VALUES"
    ]

    value_rows = []
    for _, row in df.iterrows():
        row_values = []
        for col in csv_columns:
            decoded_val = decode_hex(row[col])
            if decoded_val == "" or decoded_val.upper() == "NULL":
                row_values.append("NULL")
            else:
                try:
                    float(decoded_val)
                    row_values.append(decoded_val)
                except ValueError:
                    safe_val = str(decoded_val).replace("'", "''")
                    row_values.append(f"'{safe_val}'")
        value_rows.append(f"({', '.join(row_values)})")

    sql_statements.append(",\n".join(value_rows) + ";")

    with open(output_sql_path, "w", encoding="utf-8") as sql_file:
        sql_file.write("\n".join(sql_statements))
    print(f"\n✨ Success! Complete database script generated at: {output_sql_path}")


if __name__ == "__main__":
    print("=" * 60)
    print("      Adaptive Matrix CSV Data Decryption Engine      ")
    print("=" * 60)
    
    input_file = input("Enter the path to your source .csv file: ").strip().strip("'\"")
    if input_file.startswith('&'): 
        input_file = input_file[1:].strip().strip("'\"")
        
    if not os.path.exists(input_file):
        print(f"\n❌ Error: Source file not found at '{input_file}'")
    else:
        print("\nChoose conversion target:")
        print("1. Convert to Cleaned Decoded CSV (.csv)")
        print("2. Convert to Safe Database Script (.sql)")
        print("-" * 60)
        choice = input("Select option (1 or 2): ").strip()
        
        if choice == "1":
            output_file = input("\nEnter output path (Press Enter for 'decoded_stations.csv'): ").strip().strip("'\"")
            if not output_file: output_file = "decoded_stations.csv"
            convert_csv_to_csv(input_file, output_file)
        elif choice == "2":
            output_file = input("\nEnter output path (Press Enter for 'station.sql'): ").strip().strip("'\"")
            if not output_file: output_file = "station.sql"
            convert_csv_to_sql(input_file, output_file)
        else:
            print("\n❌ Invalid choice.")