import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.text.*;

public class Calculator extends JFrame implements ActionListener{
    JPanel[] row = new JPanel[6];
    boolean[] function = new boolean[4];
    double[] temporary = new double[2];
    String[][] decimal = new String[][]{{"0","0"},
                                        {"0","0"},
                                        {"0","0"}};
    JButton[] button = new JButton[17];
    String[] buttonText = {"C", "/",
                           "7", "8", "9", "*",
                           "4", "5", "6", "-",
                           "1", "2", "3", "+",
                           "0", ".", "="};
    JTextField display;
    Dimension displayDimension = new Dimension(203, 35);
    Dimension clearDimension = new Dimension(152, 50);
    Dimension buttonDimension = new Dimension(50, 50);
    Dimension zeroButDimension = new Dimension(101, 50);
    Font displayFont = new Font("Arial", Font.BOLD, 28);
    Font buttonFont = new Font("Arial", Font.PLAIN, 16);
    
    public Calculator(){
        super("Calculator");
        setResizable(false);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setBounds(800, 400, 230, 360);
        
        for(int i = 0; i < row.length; i++) row[i] = new JPanel();
        
        setLayout(new GridLayout(6,4));
        FlowLayout f1 = new FlowLayout(FlowLayout.CENTER);
        row[0].setLayout(f1);
        FlowLayout f2 = new FlowLayout(FlowLayout.CENTER,1,1);
        for(int i = 1; i < row.length; i++) row[i].setLayout(f2);
        
        for(int i = 0; i < button.length; i++){
            button[i] = new JButton(buttonText[i]);
            button[i].setFont(buttonFont);
            button[i].addActionListener(this);
        }
        
        display = new JTextField();
        display.setFont(displayFont);
        display.setEditable(false);
        display.setHorizontalAlignment(JTextField.RIGHT);
        
        display.setPreferredSize(displayDimension);
        button[0].setPreferredSize(clearDimension);
        for(int i = 1; i < 17; i++) button[i].setPreferredSize(buttonDimension);
        button[14].setPreferredSize(zeroButDimension);
        
        row[0].add(display);
        add(row[0]);
        
        for(int i = 0; i < 2; i++) row[1].add(button[i]);
        add(row[1]);
        
        for(int i = 2; i < 6; i++) row[2].add(button[i]);
        add(row[2]);
        
        for(int i = 6; i < 10; i++) row[3].add(button[i]);
        add(row[3]);
        
        for(int i = 10; i < 14; i++) row[4].add(button[i]);
        add(row[4]);
        
        for(int i = 14; i < 17; i++) row[5].add(button[i]);
        add(row[5]);
    }
    
    public void actionPerformed(ActionEvent evt){
        if(evt.getSource() == button[0]) clear();
        
        if(evt.getSource() == button[1]){
            function[3] = true;
            temporary[0] = Double.parseDouble(display.getText());
            display.setText("");
        }
        
        if(evt.getSource() == button[2]) append("7");
        
        if(evt.getSource() == button[3]) append("8");
        
        if(evt.getSource() == button[4]) append("9");
        
        if(evt.getSource() == button[5]){
            function[2] = true;
            temporary[0] = Double.parseDouble(display.getText());
            display.setText("");
        }
        
        if(evt.getSource() == button[6]) append("4");
        
        if(evt.getSource() == button[7]) append("5");
        
        if(evt.getSource() == button[8]) append("6");
        
        if(evt.getSource() == button[9]){
            function[1] = true;
            temporary[0] = Double.parseDouble(display.getText());
            display.setText("");
        }
        
        if(evt.getSource() == button[10]) append("1");
        
        if(evt.getSource() == button[11]) append("2");
        
        if(evt.getSource() == button[12]) append("3");
        
        if(evt.getSource() == button[13]){
            function[0] = true;
            temporary[0] = Double.parseDouble(display.getText());
            
            if(display.getText().contains(".")) decimal[0] = display.getText().split("\\.");
            
            display.setText("");
        }
        
        if(evt.getSource() == button[14]) append("0");
        
        if(evt.getSource() == button[15]) decimal();
        
        if(evt.getSource() == button[16]) result();
    }
    
    public void append(String num){
        if(display.getText().length() == 10) return;
        
        display.setText(display.getText() + num);
    }
    
    public void clear(){
        display.setText("");
    }
    
    public void decimal(){
        if(display.getText().contains(".")) return;
        
        display.setText(display.getText() + ".");
    }
    
    public void result(){
        DecimalFormat df = new DecimalFormat();
        double result = 0;
        int decimalPlaces = 0;
        String hashtags = "#.";
        temporary[1] = Double.parseDouble(display.getText());
        
        if(display.getText().contains(".")) decimal[1] = display.getText().split("\\.");
        
        if(function[0] == true){
            result = temporary[0] + temporary[1];
        }else if(function[1] == true){
            result = temporary[0] - temporary[1];
        }else if(function[2] == true){
            result = temporary[0] * temporary[1];
        }else if(function[3] == true){
            if(temporary[1] == 0){
                JOptionPane.showMessageDialog(null, "Cannot divide by zero.", "Error", JOptionPane.ERROR_MESSAGE);
                clear();
                return;
            }
            result = temporary[0] / temporary[1];
        }
        
        if(function[0] == true || function[1] == true){
            if(decimal[0][1].length() > decimal[1][1].length()){
                decimalPlaces = decimal[0][1].length();
            }else{
                decimalPlaces = decimal[1][1].length();
            }
        }else if(function[2] == true){
            decimalPlaces = decimal[0][1].length() + decimal[1][1].length();
        }else if(function[3] == true){
            decimalPlaces = 1;
        }
        
        if(Double.toString(result).contains("E")){
            df = new DecimalFormat("0.#######E0");
        }else{
            decimal[2] = Double.toString(result).split("\\.");
            
            if(decimal[2][0].length() + decimal[2][1].length() > 10){
                decimalPlaces = 10 - decimal[2][0].length();
            }
            
            while(decimalPlaces > 0){
                hashtags = hashtags + "#";
                decimalPlaces--;
            }
            
            df = new DecimalFormat(hashtags);
        }
        
        display.setText(df.format(result));
        
        for(int i = 0; i < function.length; i++){
            function[i] = false;
        }
    }
    
    public static void main(String[] args){
        Calculator demo = new Calculator();
        
        demo.setVisible(true);
    }
}