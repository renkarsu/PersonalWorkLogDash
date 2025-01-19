import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import io
import base64
from datetime import datetime, timedelta

app = dash.Dash(__name__, external_stylesheets=['/assets/styles.css'])

# Sample data for the table
sample_data = pd.DataFrame({
    '日付': pd.date_range(start='2023-01-01', periods=10, freq='D'),
    '業務内容': ['Task A', 'Task B', 'Task C', 'Task A', 'Task B', 'Task C', 'Task A', 'Task B', 'Task C', 'Task A'],
    'サブカテゴリ': ['Sub A', 'Sub A', 'Sub A', 'Sub C', 'Sub B', 'Sub B', 'Sub A', 'Sub C', 'Sub B', 'Sub A'],
    '経過時間': [1.5, 2.0, 3.0, 1.5, 2.0, 3.0, 1.5, 2.0, 3.0, 1.5],
    '成果': ['Result A', 'Result B', 'Result C', 'Result A', 'Result B', 'Result C', 'Result A', 'Result B', 'Result C', 'Result A']
})

# Sample options for the dropdown
sample_dropdown_options = [{'label': i, 'value': i} for i in sample_data['業務内容'].unique()]

# Sample figure for the graphs
sample_fig = px.pie(sample_data.groupby('業務内容', as_index=False)['経過時間'].sum(), values='経過時間', names='業務内容', title='業務内容の割合')
sample_fig.update_traces(textinfo='percent+label', texttemplate='%{label}<br>%{percent}<br>%{value} 分', hovertemplate='%{label}<br>%{percent}<br>%{value} 分')

# Sample figure for the subcategory pie chart
sample_subcategory_fig = px.pie(sample_data[sample_data['業務内容'] == 'Task A'].groupby('サブカテゴリ', as_index=False)['経過時間'].sum(), values='経過時間', names='サブカテゴリ', title='Task Aのサブカテゴリの割合')
sample_subcategory_fig.update_traces(textinfo='percent+label', texttemplate='%{label}<br>%{percent}<br>%{value} 分', hovertemplate='%{label}<br>%{percent}<br>%{value} 分')

# Sample figure for the tree diagram
sample_tree_fig = px.treemap(sample_data, path=['業務内容', 'サブカテゴリ'], values='経過時間', title='業務内容とサブカテゴリの階層構造')

app.layout = html.Div([
    html.Div(dcc.Graph(id='pie-chart', figure=sample_fig), style={'border': '1px solid black', 'padding': '10px'}),
    html.Div([
        html.H3("個人業務可視化ツール"),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        html.Div([
            dcc.DatePickerSingle(
                id='start-date-picker',
                placeholder="Start Date",
                display_format='YYYY-MM-DD'
            ),
            dcc.DatePickerSingle(
                id='end-date-picker',
                placeholder="End Date",
                display_format='YYYY-MM-DD'
            )
        ], style={'display': 'flex', 'gap': '10px'}),
        dcc.Dropdown(
            id='sample-dropdown',
            options=sample_dropdown_options,
            value='Task A',  # Set initial value to 'Task A'
            placeholder="Select an option"
        )
    ], style={'border': '1px solid black', 'padding': '10px'}),
    html.Div(dcc.Graph(id='tree-chart', figure=sample_tree_fig), style={'border': '1px solid black', 'padding': '10px'}),  # 1行3列目
    html.Div(dcc.Graph(id='pie-chart-2', figure=sample_subcategory_fig), style={'border': '1px solid black', 'padding': '10px'}),
    html.Div("2行2列目", style={'border': '1px solid black', 'padding': '10px'}),
    html.Div("2行3列目", style={'border': '1px solid black', 'padding': '10px'}),
    html.Div([
        html.Div(id='single_area', children=[
            html.H5("Sample Data"),
            html.Div([
                html.Table([
                    html.Thead(
                        html.Tr([html.Th(col, style={'padding': '10px'}) for col in sample_data.columns])
                    ),
                    html.Tbody([
                        html.Tr([
                            html.Td(sample_data.iloc[i][col], style={'padding': '10px'}) for col in sample_data.columns
                        ]) for i in range(len(sample_data))
                    ])
                ])
            ], style={'maxHeight': '400px', 'overflowY': 'scroll'})
        ])
    ], style={'border': '1px solid black', 'padding': '10px', 'gridColumn': 'span 3'}),
], style={'display': 'grid', 'gridTemplateColumns': 'repeat(3, 1fr)', 'gridTemplateRows': 'repeat(3, 1fr)', 'gap': '10px'})

def time_to_minutes(t):
    return t.hour * 60 + t.minute

def parse_contents(contents, filename, start_date, end_date):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
            print(df.head())  # Debugging: Print the first few rows of the DataFrame
            df['日付'] = pd.to_datetime(df['日付'], errors='coerce').dt.date  # Ensure 日付 is converted to datetime.date
            print(df['日付'].head())  # Debugging: Print the first few rows of the 日付 column after conversion
            if start_date and end_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                df = df[(df['日付'] >= start_date) & (df['日付'] <= end_date)]
            df['経過時間'] = df['経過時間'].apply(time_to_minutes)  # Convert 経過時間 to total minutes
            df_grouped = df.groupby('業務内容', as_index=False)['経過時間'].sum()  # Group by 業務内容 and sum 経過時間
            print(df_grouped)  # Debugging: Print the grouped DataFrame
        else:
            return {}, html.Div(['Unsupported file format']), [], pd.DataFrame()
    except Exception as e:
        return {}, html.Div([f'Error processing file: {str(e)}']), [], pd.DataFrame()

    fig = px.pie(df_grouped, values='経過時間', names='業務内容', title='業務内容の割合',
                 hover_data={'経過時間': True}, labels={'経過時間': '経過時間 (分)'})
    fig.update_traces(textinfo='percent+label', texttemplate='%{label}<br>%{percent}<br>%{value} 分', hovertemplate='%{label}<br>%{percent}<br>%{value} 分')
    dropdown_options = [{'label': i, 'value': i} for i in df_grouped['業務内容']]
    initial_value = df_grouped['業務内容'].iloc[0] if not df_grouped.empty else 'Task A'
    return fig, html.Div([
        html.H5(filename),
        html.Div([
            html.Table([
                html.Thead(
                    html.Tr([html.Th(col, style={'padding': '10px'}) for col in df.columns])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(df.iloc[i][col], style={'padding': '10px'}) for col in df.columns
                    ]) for i in range(len(df))
                ])
            ])
        ], style={'maxHeight': '400px', 'overflowY': 'scroll'})
    ]), dropdown_options, initial_value, df

@app.callback([Output('pie-chart', 'figure'), Output('single_area', 'children'), Output('sample-dropdown', 'options'), Output('sample-dropdown', 'value'), Output('pie-chart-2', 'figure'), Output('tree-chart', 'figure')],
              [Input('upload-data', 'contents'),
               Input('start-date-picker', 'date'),
               Input('end-date-picker', 'date'),
               Input('sample-dropdown', 'value')],
              State('upload-data', 'filename'))
def update_output(contents, start_date, end_date, selected_task, filename):
    fig = sample_fig  # Initialize with sample figure
    dropdown_options = sample_dropdown_options  # Initialize with sample dropdown options
    initial_value = 'Task A'  # Initialize with sample initial value
    fig2 = sample_subcategory_fig  # Initialize with sample subcategory figure
    tree_fig = sample_tree_fig  # Initialize with sample tree figure
    if contents is not None:
        fig, children, dropdown_options, initial_value, df = parse_contents(contents, filename, start_date, end_date)
        if fig is not None:
            if selected_task is None:
                selected_task = initial_value
            df_filtered = df[df['業務内容'] == selected_task]
            df_subcategory_grouped = df_filtered.groupby('サブカテゴリ', as_index=False)['経過時間'].sum()
            fig2 = px.pie(df_subcategory_grouped, values='経過時間', names='サブカテゴリ', title=f'{selected_task}のサブカテゴリの割合',
                          hover_data={'経過時間': True}, labels={'経過時間': '経過時間 (分)'})
            fig2.update_traces(textinfo='percent+label', texttemplate='%{label}<br>%{percent}<br>%{value} 分', hovertemplate='%{label}<br>%{percent}<br>%{value} 分')
            tree_fig = px.treemap(df, path=['業務内容', 'サブカテゴリ'], values='経過時間', title='業務内容とサブカテゴリの階層構造')
            return fig, children, dropdown_options, selected_task, fig2, tree_fig
    if selected_task:
        df_filtered = sample_data[sample_data['業務内容'] == selected_task]
        df_subcategory_grouped = df_filtered.groupby('サブカテゴリ', as_index=False)['経過時間'].sum()
        fig2 = px.pie(df_subcategory_grouped, values='経過時間', names='サブカテゴリ', title=f'{selected_task}のサブカテゴリの割合',
                      hover_data={'経過時間': True}, labels={'経過時間': '経過時間 (分)'})
        fig2.update_traces(textinfo='percent+label', texttemplate='%{label}<br>%{percent}<br>%{value} 分', hovertemplate='%{label}<br>%{percent}<br>%{value} 分')
        tree_fig = px.treemap(sample_data, path=['業務内容', 'サブカテゴリ'], values='経過時間', title='業務内容とサブカテゴリの階層構造')
    return fig, html.Div([
        html.H5("Sample Data"),
        html.Div([
            html.Table([
                html.Thead(
                    html.Tr([html.Th(col, style={'padding': '10px'}) for col in sample_data.columns])
                ),
                html.Tbody([
                    html.Tr([
                        html.Td(sample_data.iloc[i][col], style={'padding': '10px'}) for col in sample_data.columns
                    ]) for i in range(len(sample_data))
                ])
            ])
        ], style={'maxHeight': '400px', 'overflowY': 'scroll'})
    ]), dropdown_options, selected_task, fig2, tree_fig

if __name__ == '__main__':
    app.run_server(debug=True)
