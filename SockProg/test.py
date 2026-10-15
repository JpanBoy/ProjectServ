def main():
    attendance_pts = float(input("First Slot: "))
    project_pts = float(input("Second Slot: "))
    midterm_pts = float(input("Third Slot: "))
    final_pts = float(input("Forth Slot: "))
    
    total_pts = attendance_pts + (project_pts * 0.3) + ((midterm_pts / 66) * 30) + (final_pts * 0.5)
    
    print(f"Your ComOrg: {total_pts}")
    print(f"Your Practice: {project_pts}")
    
    
if __name__ == "__main__":
    main()