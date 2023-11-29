import os
from perlin_noise import *
from landscape import *
from flask import redirect, request, send_file, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

FORMAT = ""
LANG = ""

def delete_old_files(format):
    for filename in os.listdir('static'):
        if filename.endswith(format) and filename != "landscape17.png":
            os.remove(os.path.join('static', filename))

@app.route("/")
def home():
    session['delete_files'] = True
    return render_template("eng_main.html")

@app.route('/process-landscape', methods=['POST'])
def process_landscape():
    try:
        session["error_message"] = None
        max_height = request.form["max_height"]
        max_height = int(max_height)
        seed = request.form["numberInput"]
        size = request.form["size"]
        size_of_side = request.form["chunk_size"]
        octaves = request.form["octaves"]
        octaves = int(octaves)
        size = int(size.split("x")[0])
        size_of_side = int(size_of_side.split("x")[0])
    except:
        return render_template('eng_landscape.html', error_message="Please enter the desired parameter values")

    if isinstance(octaves, str):
        return render_template('eng_landscape.html', error_message="Please enter the desired parameter values")

    if size >= size_of_side and size_of_side >= 2 ** octaves:

        map = create_landscape_map(seed, size, size_of_side, octaves)

        if FORMAT == "PNG":
            prefix = seed + "_" + str(size) + "_" + str(size_of_side) + "_" + str(octaves) + "_landscape"
            file_path = prefix + '.png'
            try:
                # draw_image(map, file_path, size)
                print(max_height)
                # convert_landscape_map_to_image(map, size, file_path, max_height=max_height)
                draw_image_2(map, file_path, size, max_height)
                # delete_old_files('.png')
            except Exception as e:
                if LANG == 'eng' or LANG == "":
                    error_message = "Invalid color input/parameter input"
                    session["error_message"] = error_message
                    print(e)
                    return render_template('eng_main.html', error_message=session["error_message"])

            dst_folder = 'perlin/static/' + file_path
            session["user_data_png"] = dst_folder
            session["error_message"] = None

            return render_template("result.html", image_filename=file_path, error_message=session["error_message"])

        elif FORMAT == "BMP":
            prefix = seed + "_" + str(size) + "_" + str(size_of_side) + "_" + str(octaves) + "_landscape"
            file_path = prefix + '.bmp'
            try:
                # convert_landscape_map_to_image(map, size, file_path, max_height)
                draw_image_2(map, file_path, size, max_height)
                # delete_old_files('.jpeg')
            except:
                if LANG == 'eng' or LANG == "":
                    error_message = "Invalid color input/parameter input"
                    session["error_message"] = error_message
                    return render_template('eng_landscape.html', error_message=session["error_message"])

            dst_folder = 'perlin/static/' + file_path
            session["user_data_bmp"] = dst_folder
            session["error_message"] = None

            return render_template("result.html", image_filename=file_path, error_message=session["error_message"])

        else:
            if LANG == 'eng' or LANG == "":
                error_message = "Please select generation format (PNG or JPEG)."
                session["error_message"] = error_message
                return render_template('eng_landscape.html', error_message=session["error_message"])

    else:
        if LANG == 'eng' or LANG == "":
            error_message = "Please select valid values for the parametres according to formula."
            session["error_message"] = error_message
            return render_template('eng_landscape.html', error_message=session["error_message"])

@app.route('/process-parametres', methods=['POST'])
def process_parametres():
    try:
        session["error_message"] = None
        # delete_old_files()
        color = request.form["colorInput"]
        seed = request.form["numberInput"]
        size = request.form["size"]
        size_of_side = request.form["chunk_size"]
        octaves = request.form["octaves"]
        octaves = int(octaves)
        size = int(size.split("x")[0])
        size_of_side = int(size_of_side.split("x")[0])
        colors = convert_to_colors(color)
    except:
        return render_template('eng_main.html', error_message="Please, enter the desired parameter values")

    if size >= size_of_side and size_of_side >= 2 ** octaves:

        perlin_noise = create_Perlin_noise(seed, size, size_of_side, octaves)

        if FORMAT == "PNG":
            prefix = seed + "_" + str(size) + "_" + str(size_of_side) + "_" + str(octaves) + "_perlin"
            file_path = prefix + '.png'
            try:
                convert_to_image(perlin_noise, size, file_path, colors)
                # delete_old_files('.png')
            except:
                if LANG == 'eng' or LANG == "":
                    error_message = "Invalid color input/parameter input"
                    session["error_message"] = error_message
                    return render_template('eng_main.html', error_message=session["error_message"])

            dst_folder = 'perlin/static/' + file_path
            session["user_data_png"] = dst_folder
            session["error_message"] = None

            return render_template("result.html", image_filename=file_path, error_message=session["error_message"])

        elif FORMAT == "JPEG":
            prefix = seed + "_" + str(size) + "_" + str(size_of_side) + "_" + str(octaves) + "_perlin"
            file_path = prefix + '.jpeg'
            try:
                convert_to_image(perlin_noise, size, file_path, colors)
                # delete_old_files('.jpeg')
            except:
                if LANG == 'eng' or LANG == "":
                    error_message = "Invalid color input/parameter input"
                    session["error_message"] = error_message
                    return render_template('eng_main.html', error_message=session["error_message"])

            dst_folder = 'perlin/static/' + file_path
            session["user_data_jpeg"] = dst_folder
            session["error_message"] = None

            return render_template("result.html", image_filename=file_path, error_message=session["error_message"])

        else:
            if LANG == 'eng' or LANG == "":
                error_message = "Please select generation format (PNG or JPEG)."
                session["error_message"] = error_message
                return render_template('eng_main.html', error_message=session["error_message"])

    else:
        if LANG == 'eng' or LANG == "":
            error_message = "Please select valid values for the parametres according to formula."
            session["error_message"] = error_message
            return render_template('eng_main.html', error_message=session["error_message"])

@app.route('/download', methods=['POST'])
def download():
    session["error_message"] = None
    if FORMAT == "PNG":
        try:
            if os.path.exists(session["user_data_png"]):
                session["error_message"] = None
                return send_file(session["user_data_png"][7:], mimetype='image/png', as_attachment=True)
            else:
                error_message = "No file with this extension exits, you should generate it first."
                session["error_message"] = error_message
                return render_template('eng_main.html', error_message=session["error_message"])
        except Exception as e:
            print(e)
            print(session["user_data_png"])
            error_message = "No file with this extension exits, you should generate it first."
            session["error_message"] = error_message
            return render_template('eng_main.html', error_message=session["error_message"])

    if FORMAT == "JPEG":
        try:
            if os.path.exists(session["user_data_jpeg"]):
                session["error_message"] = None
                return send_file(session["user_data_jpeg"][7:], mimetype='image/jpeg', as_attachment=True)
            else:
                error_message = "No file with this extension exits, you should generate it first."
                session["error_message"] = error_message
                return render_template('eng_main.html', error_message=session["error_message"])
        except Exception as e:
            print(e)
            error_message = "No file with this extension exits, you should generate it first."
            session["error_message"] = error_message
            return render_template('eng_main.html', error_message=session["error_message"])

    if FORMAT == "BMP":
        try:
            if os.path.exists(session["user_data_bmp"]):
                session["error_message"] = None
                return send_file(session["user_data_bmp"][7:], mimetype='image/jpeg', as_attachment=True)
            else:
                error_message = "No file with this extension exits, you should generate it first."
                session["error_message"] = error_message
                return render_template('eng_main.html', error_message=session["error_message"])
        except Exception as e:
            print(e)
            error_message = "No file with this extension exits, you should generate it first."
            session["error_message"] = error_message
            return render_template('eng_main.html', error_message=session["error_message"])

    return ('', 204)

@app.route("/format-change", methods=["POST"])
def change_format():
    format = request.form['format']
    global FORMAT
    FORMAT = format
    return ('', 204)

@app.route('/perling-noise-eng')
def perling_noise_eng():
    return render_template('eng_main.html')

@app.route('/landscape-generation-eng')
def landscape_generation_eng():
    return render_template('eng_landscape.html')



if __name__ == "__main__":
    app.run(debug=True)